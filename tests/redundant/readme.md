The tests in this directory are old tests that run with python's
unittest, and for which we have already written better tests based on
pytest.

For example, you could run:

```sh
python -m unittest tests.redundant.test_seqgroup
```

In the future, if we are comfortable enough with just using pytest, we
could remove this directory.
