import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// WebGL (Three.js) no render headless
Config.setChromiumOpenGlRenderer("angle");
