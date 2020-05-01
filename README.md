# filecollector

![build](https://github.com/oleewere/filecollector/workflows/build/badge.svg)
[![PyPI version](https://badge.fury.io/py/filecollector.svg)](https://badge.fury.io/py/filecollector)

Service for collecting and processing files (with hooks)

## Features

- collect files and compress them (on command)
- anonymization
- run custom scripts on output file / processed files
- start/stop simple fileserver (at collect output location)
- stream collected files to fluentd (line by line)

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

### Simple configuration example

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

Running simple example:

```bash
# start collector 
filecollector collector start --config example/filecollector.yaml -p /my/pid/dir
# start server for browsing
filecollector server start --config example/filecollector.yaml -p /my/pid/dir
```

### Fluentd configuration example

```yaml
collector:
    files:
    - path: "example/example*.txt"
      label: "txt"
    rules:
    - pattern:  \d{4}[^\w]\d{4}[^\w]\d{4}[^\w]\d{4}
      replacement: "[REDACTED]"
    compress: false
    useFullPath: true
    deleteProcessedTempFilesOneByOne: true
    outputLocation: "example/files"
    processor:
      host: "localhost"
      port: 24224
      tag: example
```

Fluentd configuration:

```
<source>
  @type forward
  port 24224
  bind 0.0.0.0
</source>

<match example.**>
   @type stdout
</match>
```

Running fluentd example:

```bash
# start fluentd 
fluentd --config example/fluentd.conf
# start collector 
filecollector collector start --config example/fluentd-filecollector.yaml -p /my/pid/dir
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

#### `collector.preProcessScript`

Script that runs before the files are collected. It gets the folder name (where the files are processed) as an input.

#### `collector.outputScript`

Script that runs once with the compressed output file name as an input.

#### `collector.deleteProcessedTempFiles`

After collection of the files + compression, the collected files are deleted. Can be useful to disable this behaviour `compress` option is disabled. Default value is `true`.

#### `collector.deleteProcessedTempFilesOneByOne`

If this option is set, files are deleted right after processed (one at a time). That can be useful if compression is disabled, and you would like to stream large files to fluentd. Default value is `false`.

#### `collector.fluentProcessor`

Fluentd related section for processing files line by line - streaming data by fluentd forward protocol.

#### `collector.fluentProcessor.host`

Fluentd host (for forward protocol). Default value: `localhost`.

#### `collector.fluentProcessor.port`

Fluentd port (for forward protocol). Default value: `24224`.

#### `collector.fluentProcessor.tag`

Fluentd tag for streaming lines. The generated tag for forward protocol is `<collector.fluentProcessor.tag>.<file label for monitored file>`.

#### `collector.fluentProcessor.messageField`

The processed lines are mapped for this field before data has been sent to Fluentd. Default value: `message`.

#### `collector.fluentProcessor.includeTime`

If this is enabled, current time is included in the fluentd data event. (as `time` field). Default value: `false`.

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request
