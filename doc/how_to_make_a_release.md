# How to make a release of tuttle


1. Make sure the changelog (CHANGELOG.MD) is up to date
1. Make sure the ```Build version format``` in [Appveyor](https://ci.appveyor.com/project/lexman/tuttle/settings) is up to date with the intended release version, eg ```0.3-{build}```
1. Change the version number in file ```tuttle/VERSION```, eg ```0.3-rc0```
1. Update the debian version of the package :
  * Add the new version and the changelog in the file debian/changelog
  * Update travis.yml to follow the new version number in the package name. Package name is in
    - the name of the file to push to github release (line ```file: dist/debian/tuttle_0.3-1_amd64.deb```)
    - the command line to deploy the package to test (line ```- sudo dpkg -i dist/debian/tuttle_0.3-1_amd64.deb```)
1. Make sure everything has been pushed and all the tests pass on both [Appveyor](https://ci.appveyor.com/project/lexman/tuttle) (windows) and [Travis](travis-ci.org/lexman/tuttle)
1. Create a new RC tag for the intended version, eg ```v0.3-rc0```
1. Push the tag :
  * Github will create a new release
  * Travis will make the deb64 package and push it to github release
  * Appveyor will create the win32 and win64 packages and will save save them localy
1. Finish the release on github :
  * download win32 and win64 packages from appveyor and copy them to Github release
  * Compile a deb32 package on a debian environment and upload it to Github release
  * Copy and Paste the release changelog to Github release

1. Make new RCs until ready... And eventually make a final version.
1. Make the version in ```tuttle/VERSION``` ready for next release, eg ```0.4-pre```
1. Make ```Build version format``` in (Appveyor)[https://ci.appveyor.com/project/lexman/tuttle/settings] ready for next release, eg ```0.4-{build}```
