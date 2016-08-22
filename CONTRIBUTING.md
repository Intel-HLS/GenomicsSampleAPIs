#How to contribute

## Thank you!

We are excited you are interested in improving the sample APIs  Thanks for taking the interest and time!

## Code Layout

The code layout is descrived in the [README](https://github.com/Intel-HLS/GenomicsSampleAPIs/blob/spec_tests/README.md#repository-organization).

## Code Style

We are somewhat loose on coding style.  Generally try to stay consistant with the naming, spacing, and layout of the language as used thus far.

### Python

Generally [pep8](https://www.python.org/dev/peps/pep-0008) is a good goal, but not an absolute requirement.  Line length is done for readability, so not strictly 79 chars.

- Functions are usually named with under_scores or mixedCase.
- Classes are usually named with CapitalizedWords
- variables are usually named with lowercase
- autoflake and autopep are useful tools to get the broad strokes.

### C / C++

## Pull Request Workflow

1. Pull Requests should be limited to a feature or bug fix.
2. Create a branch in which to work. 
3. Submit a PR back to master.
4. Once it is tested and checked, the PR can be accepted and merged into master.

## Testing

Best effort should be made to maintain or improve the code coverage with each PR.  Pleast write new unit tests were appropriate for new functions.

### Automation

To test the ansible code, and perform end to end testing, we use serverspec.  Please write new tests to cover new functionality, endpoints, edge cases, and install artifacts.  For examples, see the spec directory in each role under [infrastructure/ansible](https://github.com/Intel-HLS/GenomicsSampleAPIs/tree/master/infrastructure/ansible/roles).

### Unit

For python use pytest.

## Questions

### FAQ

To be added as questions are frequently asked

### Answers

If you have any questsions, checkout out the [Questions](#Questions) section.  Most of our documentation is in the project [wiki](https://github.com/Intel-HLS/GenomicsSampleAPIs/wiki)

If you have any further questions, contact the project [maintainers or authors](https://github.com/Intel-HLS/GenomicsSampleAPIs/blob/master/AUTHORS).


