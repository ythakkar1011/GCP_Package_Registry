# ECE 461 Project 1

This system is simply an analyzer for the open-source modules. The user specifies the URL links to their desired modules in a file and then runs the software by passing that URL file as an argument. The system does the necessary parsing of the file and starts working on gathering necessary information about the repositories one by one. It computes scores for each of the user-defined metrics (ramp-up, correctness, bus-factor, responsive-maintainer, license scores) and gives the user the resulting scores for each along with a net score. The system also implements unit-testing which can be run by the user.

## Installation

For installing all the dependencies, run the following command:

```bash
./run install
```

## Usage

Step-1) Create a URL file for your repositories (URLs should be in seperate lines)  
Step-2) ```./run <URL_filename> ```

## Testing
Use the following command for unit-testing and line-coverage results.

```bash
./run test
```
