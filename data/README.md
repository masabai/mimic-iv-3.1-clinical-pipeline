#### Alternative: Pull Custom Mappings Directly from CogStack
If you did not clone the custom mappings recursively, execute this terminal command to fetch the community lookup maps directly from the CogStack primary source repository:

```bash
# Create the local data subdirectory
mkdir -p cog/custom_mappings

# Download and extract the GCPT lookup map sheets automatically
curl -sL https://github.com/CogStack/dbt_mimic_omop/tree/main/data/custom_mappings \
  | tar -xz --strip-components=3 -C cog/custom_mappings --wildcards "*/cog/custom_mappings/*.csv"
```


Custom mapping CSVs are sourced directly from the CogStack dbt_mimic_omop repository.
Clone or download from: 

https://github.com/CogStack/dbt_mimic_omop/archive/refs/heads/main.tar.gz/

Place CSVs into: data/custom_mappings/
