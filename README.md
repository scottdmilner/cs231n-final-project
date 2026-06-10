# For TAs
- The optimization loop and hyperparameter tuning workspace can be found in `harness.ipynb`
- Code that we wrote can be found in `src/`
- Code from others (cited in our paper) can be found in `external/` alongside our custom patches for it.
- Since StyleID is Stable Diffusion-based, in order for the StyleInjection method to work (1 of 5 methods), the Stable Diffusion weights need to be placed in the appropriate spot in `models`. Not included as they are 4GB.
- To minimize upload size, we have only included a small fraction of our training data
- All AI usage can be found as chat transcripts in `AI Chat Logs/`

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
