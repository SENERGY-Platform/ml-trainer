#!/bin/bash
python -m uvicorn model_trainer.app:app --host 0.0.0.0 --port 5000
