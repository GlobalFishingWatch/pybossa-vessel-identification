
upload the json files.
```bash
gsutil mv * gs://gfw-crowd
```

make everything readable:
 
 ```bash
 gsutil -m acl set -R -a public-read  gs://gfw-crowd
 ```
