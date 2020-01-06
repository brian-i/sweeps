# sweeps
Run parameter sweeps easily, in parallel, with JSON parameters, logs, diverse language support, and parameter data frames.

## Installation
*Python **3.7** or above is required for running sweeps. Versions 3.6 and below will encounter error.*

To install: Download sweeps package, navigate to its directory (`cd sweeps`) and execute the following:
```bash
sudo python setup.py install
```

After installation, `sweeps` may now be invoked from the command line anywhere on your system.

## Usage
This guide assumes you are working in the top-level of your parameter sweeps directory. For an example, see the directory tree below.
1. Initialize this directory by creating `bin` and `rfs` directories.
2. Add a JSON file to the top-level containing parameter sweep information.
3. Add a script file to the `bin` folder.
4. Create run folders (rfs) using `sweeps create` (below)
5. Run the script using `sweeps run` (below)

### To create rfs:
Run folders (rfs) represent individual runs of a script file for a particular parameter. The folder name is a hash depending on the parameter value and script file.

```bash
sweeps . create sweep_config.json
```

### To run script:
**Requirement:** A script file, such as `script.py`, must be located inside a `bin` folder on your top-level directory. (See example directory tree below:)
```bash
sweeps . run python script_file.py
```

### To query:
Querying shows the status of your run, including the number of rfs completed, queued, running, and failed.

**Requirement:** A script file, such as `script.py`, must be located inside a `bin` folder on your top-level directory. (This is already satisfied if `sweeps run` was used.)
```bash
sweeps . query script_file.py
```

# Example Directory Structure Tree
```
.
├── bin
│   └── script_file.jl
├── history
│   ├── 2019-12-10_16-34-13.create.json
│   ├── 2019-12-10_16-34-40.run
│   └── 2019-12-10_16-34-40.script
├── rfs
│   ├── 0e37e95b8301883e
│   │   ├── log.txt
│   │   ├── params.json
│   │   └── status.txt
│   ├── 6e733249c3ae5dd1
│   │   ├── log.txt
│   │   ├── params.json
│   │   └── status.txt
│   ├── 7bfacd4db6a44d40
│   │   ├── log.txt
│   │   ├── params.json
│   │   └── status.txt
│   ├── 9ac81a2c5029aa08
│   │   ├── log.txt
│   │   ├── params.json
│   │   └── status.txt
│   └── d73ece6dc1a2f5e8
│       ├── log.txt
│       ├── params.json
│       └── status.txt
└── sweep_config.json
```