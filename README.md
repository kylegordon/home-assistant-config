![Home-Assistant](https://github.com/kylegordon/home-assistant-config/actions/workflows/main.yaml/badge.svg)  
![ESPHome](https://github.com/kylegordon/home-assistant-config/actions/workflows/esphome-parallel.yaml/badge.svg)


My Home-Assistant configuration.

An amalgamation of various examples and sources around the internet, with my own bodging holding it together.

Deployed through the use of docker-compose and the service description at https://github.com/kylegordon/ha-stack


### HWAM Stove Notes

Basic REST and template sensors can be used, such as those described at https://github.com/peterczarlarsen-ha/hwam/blob/main/configure.yaml

In this instance, the hwam_stove custom component is imported from https://github.com/mvn23/hwam_stove
