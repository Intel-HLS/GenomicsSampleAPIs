"""
  The MIT License (MIT)
  Copyright (c) 2016 Intel Corporation

  Permission is hereby granted, free of charge, to any person obtaining a copy of 
  this software and associated documentation files (the "Software"), to deal in 
  the Software without restriction, including without limitation the rights to 
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
  the Software, and to permit persons to whom the Software is furnished to do so, 
  subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all 
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import time
import uuid
from time import strftime
from sqlalchemy import create_engine, and_, or_, exc
from sqlalchemy.orm import sessionmaker
from mappingdb.models import CallSet
from mappingdb.models import CallSetToDBArrayAssociation
from mappingdb.models import DBArray
from mappingdb.models import Individual
from mappingdb.models import Reference
from mappingdb.models import ReferenceSet
from mappingdb.models import Sample
from mappingdb.models import VariantSet
from mappingdb.models import Workspace
from mappingdb.models import bind_engine
from mappingdb.models import tiledb_reference_offset_padding_factor_default
from mappingdb.models import GenomicsDSInstance
from mappingdb.models import GenomicsDSPartition
from collections import OrderedDict, namedtuple


class DBImport():
    """
    Keeps the enging and the session maker for the database
    """

    def __init__(self, database, echo_debug=False):
        self.engine = create_engine(database, echo=echo_debug)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def getSession(self):
        """
        Returns the Query object that can be used with "with" clause
        """
        return Import(self)


class Import():
    """
    Manages the session for importing
    This will be the class that verifies registration and imports data into mappingdb
    """

    def __init__(self, db):
        self.db = db

    def __enter__(self):
        self.session = self.db.Session()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def get_sqlalchemy_session(self):
        return self.session

    def registerReferenceSet(self, guid, assembly_id, source_accessions=None, description=None, references=OrderedDict(),
        tiledb_reference_offset_padding_factor=tiledb_reference_offset_padding_factor_default):
        """
        ReferenceSet registration for MAF occurs from an assembly config file. See hg19.json for example.
        ReferenceSet registration for VCF occurs from reading VCF contig tags in header.
        Requires assembly ids and guids to be unique.
        """

        referenceSet = self.session.query(ReferenceSet).filter(
            ReferenceSet.guid == guid)\
            .first()

        if referenceSet is None:

            try:
                referenceSet = ReferenceSet(
                    guid=guid, assembly_id=assembly_id, description=description,
                    tiledb_reference_offset_padding_factor=tiledb_reference_offset_padding_factor)
                self.session.add(referenceSet)
                self.session.commit()

            except exc.DataError as e:
                self.session.rollback()
                raise ValueError("{0} : {1} ".format(str(e), guid))

            if len(references) > 0:
                # use pyvcf like ordered dict to avoiding having to specify
                # reference order manually
                refs = sortReferences(references)
                for ref in refs:
                    self.registerReference(
                        str(uuid.uuid4()), referenceSet.id, ref, refs[ref].length)

        return referenceSet

    def registerReference(self, guid, reference_set_id, name, length):
        """
        Registers a Reference. Most often called by registerReferenceSet.
        Requires a Reference name be unique for all references in a reference set
        """

        reference_set_id_as_int = get_as_long(reference_set_id)
        reference_set_db_id = self.session.query(ReferenceSet.id).filter(
                or_(ReferenceSet.id == reference_set_id_as_int, ReferenceSet.guid == str(reference_set_id))
                ).first()
        if(not reference_set_db_id):
            raise ValueError(
                "ReferenceSet not found for id : {0} ".format(reference_set_id))

        reference = self.session.query(Reference).filter(
            or_(Reference.guid == guid,
                and_(Reference.reference_set_id == reference_set_db_id, Reference.name == name))
            )\
            .first()

        if reference is None:
            try:
                reference = Reference(
                    name=name,
                    reference_set_id=reference_set_db_id,
                    length=length,
                    guid=guid
                )
                self.session.add(reference)
                self.session.commit()

            except exc.DataError as e:
                self.session.rollback()
                raise ValueError("{0} : {1} ".format(str(e), guid))

        return reference

    def registerWorkspace(self, guid, name):
        """
        Registers a workspace.
        Workspace name is the path to the workspace directory. This is assumed unique per mappingdb instance.
        """

        # if the name ends with a / then remove it from the name.
        # This is done only for consistency in workspace name
        # since users could have / or not for the workspace.
        name = name.rstrip('/')

        workspace = self.session.query(Workspace).filter(
            (Workspace.guid == guid))\
            .first()

        if workspace is None:
            try:
                workspace = Workspace(
                    guid=guid,
                    name=name
                )
                self.session.add(workspace)
                self.session.commit()

            except exc.DataError as e:
                self.session.rollback()
                raise ValueError("{0} : {1} ".format(str(e), guid))

        return workspace

    def registerDBArray(self, guid, reference_set_id, workspace_id, name):
        """
        Registers a DBArray.
        An array is unique named folder in a unique workspace path and a given reference id.
        """

        workspace_id_as_int = get_as_long(workspace_id)
        workspace_db_id = self.session.query(Workspace.id).filter(
                or_(Workspace.id == workspace_id_as_int, Workspace.guid == str(workspace_id))
                ).first()

        reference_set_id_as_int = get_as_long(reference_set_id)
        reference_set_db_id = self.session.query(ReferenceSet.id).filter(
                or_(ReferenceSet.id == reference_set_id_as_int, ReferenceSet.guid == str(reference_set_id))
                ).first()

        # array is a unique combination of workspace and array
        dbarray = self.session.query(DBArray) .filter(
             or_(DBArray.guid == guid,
                 and_(DBArray.workspace_id == workspace_db_id, DBArray.name == name)))\
            .first()

        if dbarray is None:
            try:
                dbarray = DBArray(
                    guid=guid,
                    reference_set_id=reference_set_db_id,
                    workspace_id=workspace_db_id,
                    name=name
                )
                self.session.add(dbarray)
                self.session.commit()

            except exc.DataError as e:
                self.session.rollback()
                raise ValueError("{0} : {1} ".format(str(e), guid))

        return dbarray

    def registerVariantSet(self, guid, reference_set_id, dataset_id=None, metadata=None):
        """
        Register variant set.
        """

        referenceSet = self.session.query(ReferenceSet).filter(
            ReferenceSet.id == reference_set_id)\
            .first()

        if referenceSet is None:
            raise ValueError(
                "ReferenceSet must be registered before registering this VariantSet : {0} ".format(reference_set_id))

        variantSet = self.session.query(
            VariantSet).filter(VariantSet.guid == guid)\
            .first()

        if variantSet is None:
            try:
                variantSet = VariantSet(
                    guid=guid,
                    reference_set_id=reference_set_id,
                    dataset_id=dataset_id,
                    variant_set_metadata=metadata
                )
                self.session.add(variantSet)
                self.session.commit()

            except exc.DataError as e:
                self.session.rollback()
                raise ValueError("{0} : {1} ".format(str(e), guid))

        return variantSet

    def updateVariantSetList(self, variant_set_ids, callset=None):
        """
        Add a VariantSet to a callset variantset list.
        Duplicate variant sets cannot be added to a callset variant set list
        ie. set(callset.variant_sets)
        """

        variantSets = self.session.query(VariantSet).filter(
            VariantSet.id.in_(variant_set_ids))\
            .all()

        if len(variantSets) != len(variant_set_ids):
            raise ValueError(
                "VariantSet must be registered before being added to CallSet VariantSet list.")

        if callset is None:
            return variantSets

        callset.variant_sets.extend(
            x for x in variantSets if x not in callset.variant_sets)

        return callset

    def addCallSetToDBArrayAssociation(self, callset_id, db_array_id):
        """
        Register a callset to an array.
        All callsets in an array must be unique, but a callset can belong to multiple arrays.
        """

        db_array_id_as_int = get_as_long(db_array_id)
        db_array_db_id = self.session.query(DBArray.id).filter(
                or_(DBArray.id == db_array_id_as_int, DBArray.guid == str(db_array_id))
                ).first();

        callset_id_as_int = get_as_long(callset_id)
        callset_db_id = self.session.query(CallSet.id).filter(
                or_(CallSet.id == callset_id_as_int, CallSet.guid == str(callset_id))
                ).first();

        # check if callset is registered to array already
        callSetToDBArrayAssociation = self.session.query(CallSetToDBArrayAssociation) .filter(
            and_(CallSetToDBArrayAssociation.db_array_id == db_array_db_id,
                CallSetToDBArrayAssociation.callset_id == callset_db_id))\
            .first()

        if callSetToDBArrayAssociation is None:

            callSetToDBArrayAssociation = CallSetToDBArrayAssociation(
                db_array_id=db_array_db_id,
                callset_id=callset_db_id
            )
            self.session.add(callSetToDBArrayAssociation)
            self.session.commit()

    def registerCallSet(self, guid, source_sample_guid, target_sample_guid,
            info=None, name=None):
        """
        Register a callset.
        Registration requires a unique guid
        """

        # get samples
        source_sample_id_as_int = get_as_long(source_sample_guid)
        sourceSample = self.session.query(Sample.id).filter(
            or_(Sample.guid == source_sample_id_as_int, Sample.id == str(source_sample_guid)))\
            .first()
        target_sample_id_as_int = get_as_long(target_sample_guid)
        targetSample = self.session.query(Sample.id).filter(
            or_(Sample.guid == target_sample_id_as_int, Sample.id == str(target_sample_guid)))\
            .first()

        if sourceSample is None or targetSample is None:
            raise ValueError(
                "Issue retrieving Sample info, check: source sample {0}, or target sample {1}".format(
                    source_sample_guid, target_sample_guid))

        callSet = self.session.query(CallSet).filter(
            CallSet.guid == guid)\
            .first()

        if callSet is None:
            if variant_set_ids is None:
                raise ValueError(
                    "Registration of a CallSet requires association to an existing VariantSet.")

            try:
                callSet = CallSet(
                    guid=guid,
                    name=name,
                    created=int(time.time() * 1000),
                    updated=int(time.time() * 1000),
                    info=info,
                    source_sample_id=sourceSample.id,
                    target_sample_id=targetSample.id
                    )

                self.session.add(callSet)
                self.session.commit()

            except exc.DataError as e:
                self.session.rollback()
                raise ValueError("{0} : {1} ".format(str(e), guid))

        return callSet

    def registerSample(self, guid, individual_guid, name=None, info=None):
        """
        Registration of a Sample requires an individual be registered.
        Unique guid, or unique name per individual
        ie. an individual cannot have two samples with the same name
        """

        individual_id_as_int = get_as_long(individual_guid)
        individual = self.session.query(Individual).filter(
            or_(Individual.guid == str(individual_guid), Individual.id == individual_id_as_int))\
            .first()

        if individual is None:
            raise ValueError(
                "Invalid Individual Id : {0} ".format(individual_guid))

        sample = self.session.query(Sample).filter(
            Sample.guid == guid)\
            .first()

        if sample is None:
            try:
                sample = Sample(
                    guid=guid,
                    individual_id=individual.id,
                    name=name,
                    info=info
                )
                self.session.add(sample)
                self.session.commit()

            except exc.DataError as e:

                self.session.rollback()
                raise ValueError("{0} : {1} ".format(str(e), guid))

        return sample

    def registerIndividual(self, guid, name, info=None):
        """
        Registration of an individual requires a guid and a name.
        Name can be None to support retrival from registerSample
        """

        individual = self.session.query(Individual).filter(
            Individual.guid == str(guid))\
            .first()

        if individual is None:

            try:
                individual = Individual(
                    name=name,
                    guid=guid,
                    info=info,
                    record_update_time=strftime("%Y-%m-%d %H:%M:%S%S.%S%S%S"),
                    record_create_time=strftime("%Y-%m-%d %H:%M:%S%S.%S%S%S")
                )
                self.session.add(individual)
                self.session.commit()

            except (exc.DataError, exc.IntegrityError) as e:

                self.session.rollback()
                raise ValueError("{0} : {1} : {2} ".format(str(e), guid, name))

        return individual

    def registerGenomicsDSInstance(self, guid, name, reference_set_id, info=None):
        """
        Registration of a GenomicsDSInstance requires a guid and a name
        """
        genomicsds_instance = self.session.query(GenomicsDSInstance).filter(
                (GenomicsDSInstance.guid == guid)).first();

        if(not genomicsds_instance):

            reference_set_id_as_int = get_as_long(reference_set_id)
            reference_set_db_id = self.session.query(ReferenceSet.id).filter(
                    or_(ReferenceSet.id == reference_set_id_as_int,
                        ReferenceSet.guid == str(reference_set_id))
                    ).first()
            if reference_set_db_id is None:
                raise ValueError(
                        "Invalid ReferenceSetId : {0} ".format(reference_set_id))

            try:
                genomicsds_instance = GenomicsDSInstance(
                        guid=guid,
                        name=name,
                        reference_set_id=reference_set_db_id
                        )
                self.session.add(genomicsds_instance)
                self.session.commit()

            except (exc.DataError, exc.IntegrityError) as e:

                self.session.rollback()
                raise ValueError("{0} : {1} : {2} ".format(str(e), guid, name))

        return  genomicsds_instance

    def registerGenomicsDSPartition(self, guid, name, genomicsds_instance_id,
            workspace_id, db_array_id, data_store_type='tiledb_on_disk_array', info=None):
        """
        Registration of a GenomicsDSPartition requires a guid, name, genomicsds_instance_id
        workspace_id and db_array_id
        """

        genomicsds_partition = self.session.query(GenomicsDSPartition).filter(
                (GenomicsDSPartition.guid == guid)).first();

        if(not genomicsds_partition):

            genomicsds_instance_id_as_int = get_as_long(genomicsds_instance_id)
            genomicsds_instance_db_id = self.session.query(GenomicsDSInstance.id).filter(
                    or_(GenomicsDSInstance.id == genomicsds_instance_id_as_int,
                        GenomicsDSInstance.guid == str(genomicsds_instance_id))
                    ).first();

            workspace_id_as_int = get_as_long(workspace_id)
            workspace_db_id = self.session.query(Workspace.id).filter(
                    or_(Workspace.id == workspace_id_as_int, Workspace.guid == str(workspace_id))
                    ).first()

            db_array_id_as_int = get_as_long(db_array_id)
            db_array_db_id = self.session.query(DBArray.id).filter(
                    or_(DBArray.id == db_array_id_as_int, DBArray.guid == str(db_array_id))
                    ).first();

            try:
                genomicsds_partition = GenomicsDSPartition(
                        guid=guid,
                        name=name,
                        genomicsds_instance_id = genomicsds_instance_db_id,
                        workspace_id=workspace_db_id,
                        db_array_id=db_array_db_id,
                        data_store_type=data_store_type
                        )
                self.session.add(genomicsds_partition)
                self.session.commit()

            except (exc.DataError, exc.IntegrityError) as e:

                self.session.rollback()
                raise ValueError("{0} : {1} : {2} ".format(str(e), guid, name))

        return  genomicsds_partition

def sortReferences(references):
    """
    Used in registerReferenceSet to sort and represent a list of references like pyvcf.
    This removes the need user specified reference list order.
    """
    # sorting and represent a list of references like pyvcf
    Contig = namedtuple('Contig', 'id length')

    if references.__class__ != OrderedDict().__class__:
        vcflike_refs = {str(key): Contig(id=str(key), length=value)
                        for (key, value) in references.items()}
        references = OrderedDict(
            sorted(
                vcflike_refs.items(),
                key=lambda key_value: int(
                    key_value[0]) if key_value[0].isdigit() else key_value[0])
            )

    return references

def get_as_long(value):
    return long(value) if (type(value) is long or type(value) is int) else long(-1)
