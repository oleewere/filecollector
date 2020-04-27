# filecollector

![build](https://github.com/oleewere/filecollector/workflows/build/badge.svg)
[![PyPI version](https://badge.fury.io/py/filecollector.svg)](https://badge.fury.io/py/filecollector)

Service for collecting and processing files (with hooks)

## Features

- collect files and compress them (on command)
- anonymization
- run custom scripts on output file / processed files
- start/stop simple fileserver (at collect output location)

## Requirements

- python 2.7+ / python 3.5+
- pip

## Installation

```bash
pip install filecollector
```

## Usage

It has 2 main components right now: collector and server. Collector is responsible to collect/anonymize the files and run hook scripts on those. Server is only a browser for the collected files.

At the start you need to create a `yaml` configuration file for the collector.
Only this configuration is required as an input for `filecollector`.

#### Start the collector

```
filecollector collector start --config filecollector.yaml -p /my/pid/dir
```


#### Start the server

```
filecollector server start --config filecollector.yaml -p /my/pid/dir
```

### Configration

### Configuration example

```yaml
server:
    port: 1999
    folder: "../example/files" 
collector:
    files:
    - path: "example/example*.txt"
      label: "example"
    rules:
    - pattern:  \d{4}[^\w]\d{4}[^\w]\d{4}[^\w]\d{4}
      replacement: "[REDACTED]"
    processFileScript: example/scripts/process_file.sh
    compress: true
    useFullPath: true
    outputScript: example/scripts/output_file.sh
    processFilesFolderScript: example/scripts/tmp_folder.sh
    deleteProcessedTemplateFiles: true
    outputLocation: "example/files"
```

### Configuration options

#### `server`

The server block, it contains configurations related with the filecollector server component.

#### `server.port`

Port that will be used by the filecollector server.

#### `server.folder`

The folder that is server by the file server.

#### `collector`

The collector block, it contains configurations related with the filecollector collector component.

#### `collector.files`

List of files (with `name` and `label`) that needs to be collected. The `name` options can be used as wildcards.

#### `collector.rules`

List of anonymization rules that can be run against the file inputs. (`pattern` field for matching, `replacement` for the replacement on match)

#### `collector.compress`

At the end of the filecollection, the output folder is compressed. The default value is `true`.

#### `collector.compressFormat`

Compression format, possible values: `zip`, `tar`, `gztar`, `bztar`. Default value is `zip`.

#### `collector.outputLocation`

Output location (directory), where the processed file(s) will be stored.

#### `collector.useFullPath`

Use full path for processed files (inside `outputLocation`). Can be useful if because of the wildcard patterns, the base file name are the same for different files from different folders. Default value is `true`.

#### `collector.processFileScript`

Script that runs agains 1 processed file. It gets the filename and the label for a processed file.

#### `collector.processFilesFolderScript`

Script that runs once after the files are collected. It gets the folder name (where the files are processed) as an input.

#### `collector.outputScript`

Script that runs once with the compressed output file name as an input.

#### `collector.deleteProcessedTemplateFiles`

After collection of the files + compression, the collected files are deleted. Can be useful to disable this behaviour `compress` option is disabled. Default value is `true`.

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
