# Common Pitfalls


## Linux-based systems

### `ModuleNotFoundError: No module named 'distutils.util'`
If ``poetry install` throws out a bunch of errors that look like this,
and you are on a Debian-based system, try this command

```bash
sudo apt-get install python3-distutils
```

> Note: If you are using the deadsnakes ppa, you will need the specific version. 
> For example, 
> ```bash
> sudo apt-get install python3.9-distutils
> ```

### `Python.h not found` when poetry tries to install `pysqlite3`

Most likely, you are missing `python3-dev`, the development headers for Python.
Simply 

```bash
sudo apt-get install python3-dev
```

Again, same note as above for deadsnakes ppa users, replace `python3` with `python3.9` or so.


### Poetry created the virtualenv with the wrong version of Python!
If you have `python3.9` in your path, simply do
`poetry env use 3.9` to switch to the correct version. You might need to run `poetry install` again.

If you are using pyenv, see the [main contributing doc](./CONTRIBUTING.md) for more info.