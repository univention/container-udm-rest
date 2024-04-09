# Utility `dockpin`

This folder defines a utility container image which is based on the Univention
base image and does include the utility `dockpin`, so that this tool can be used
to lock Apt based dependencies.

## Status - EXPERIMENTAL

This image is serving an experiment.

If it should be intended for usage then it must be moved into a more appropriate
place like the repository of the ucs based image.

## Usage

The main idea is to allow to use `dockpin` together with the Univention sources
in an easy way.

Compare the README of `dockpin` itself:
<https://github.com/Jille/dockpin/blob/master/README.md>
