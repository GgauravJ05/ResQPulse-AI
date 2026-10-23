# ResQPulse AI: common commands. Run from the repo root with the virtual environment active.
PY ?= python

.PHONY: help install api api-fake ui test eval data gold public-dataset kaggle-metadata kaggle-release

help:            ## list commands
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-16s %s\n", $$1, $$2}'

install:         ## install Python dependencies
	$(PY) -m pip install -r requirements.txt

api:             ## start the backend with the real models (needs models/)
	USE_FAKE_MODELS=false $(PY) -m uvicorn src.api.main:app --port 8000

api-fake:        ## start the backend with fake models (no weights needed)
	USE_FAKE_MODELS=true $(PY) -m uvicorn src.api.main:app --port 8000

ui:              ## start the dashboard on http://localhost:8501
	$(PY) -m streamlit run app/streamlit_app.py

test:            ## run the test suite
	$(PY) -m pytest tests -q

data:            ## validate synthetic reports, clean public data, build the splits (needs data/raw/, see README)
	$(PY) scripts/validate_synthetic.py
	$(PY) scripts/build_public.py
	$(PY) scripts/make_splits.py

gold:            ## rebuild the gold test set text from the public data by ID
	$(PY) scripts/rehydrate_gold.py

eval:            ## score every prediction file in predictions/ and write reports/
	$(PY) scripts/evaluate.py

public-dataset:  ## build the redistributable dataset release in dist/kaggle/
	$(PY) scripts/make_public_dataset.py

kaggle-metadata: public-dataset  ## write dist/kaggle/dataset-metadata.json from docs/KAGGLE_DATACARD.md
	$(PY) scripts/make_kaggle_metadata.py

kaggle-release: kaggle-metadata  ## upload dist/kaggle/ as a new Kaggle version (needs the kaggle CLI + API token); MSG="..."
	kaggle datasets version -p dist/kaggle -m "$(or $(MSG),Update from docs/KAGGLE_DATACARD.md)"
	kaggle datasets metadata --update -p dist/kaggle ggauravj05/resqpulse-data
