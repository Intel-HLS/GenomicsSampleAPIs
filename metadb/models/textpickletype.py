import sqlalchemy as sa


class TextPickleType(sa.PickleType):
    impl = sa.Text
