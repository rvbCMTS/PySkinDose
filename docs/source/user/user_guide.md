# User guide

## Running PySkinDose headless

Sometimes you might want to run PySkinDose without having to look at the output immediately. This might, for example, be the case if you want to automate the PySkinDose calculations. In this case you can have a script that runs the `analyze_normalized_data_with_custom_settings_object` (see incomplete example below).

```python
import pandas as pd
from pyskindose import analyze_normalized_data_with_custom_settings_object

settings = '<the-entire-settings-file-as-json-string>'
normalized_data = pd.DataFrame(columns=[
    
])  # "<Your normalized data as a pandas DataFrame>"

result = analyze_normalized_data_with_custom_settings_object(
    data_norm=normalized_data,
    settings=settings,
    output_format="json"  # Valid values are "json" and "dict"
)
```
