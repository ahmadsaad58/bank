# Utils Folder

This folder contains utility functions and helper modules used throughout the Simple Bank API project.

## Structure

- `utils.py` — General-purpose utility functions
- (Add other utility modules here as needed.)

## Purpose

The utils folder is intended for reusable code that does not belong to a specific model or API endpoint.

## Usage

Import functions from this folder wherever you need shared logic. For example:

```python
from bank.utils.utils import parse_boolean_query_param
```