## Dev setup


```bash
# Clone the repo
git clone --recurse-submodules git@github.com:scottdmilner/cs231n-final-project.git

# install OpenVDB build dependencies
HOMEBREW_NO_AUTO_UPDATE=1 brew install boost c-blosc jemalloc ninja openexr tbb

# download and build python packages
uv sync

# activate Python venv
source .venv/bin/activate
```


Running `uv sync` will build all external packages with their Python bindings and install all project Python dependencies into `.venv`. The OpenVDB build may have other dependencies you need to install in order to get a successful sync.
