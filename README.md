# TeSSLa plugin for Home Assistant

This is the TeSSLa plugin for Home Assistant. Send and recieve data from Home Assistant to TeSSLa.

## Prerequisites

Before you begin, make sure you have the following prerequisites installed on your system:

- [Home Assistant](https://www.home-assistant.io/) installed either on a physical device or in a container.
- Java installed on your system.
- The [TESSLA interpreter](https://www.tessla.io/) in the form of a JAR file called `tessla.jar`. Place this file in the same folder as the plugin.

## Installation

**Dependencies:**

- Java: You need Java to run TeSSLa.
- TeSSLa interpreter JAR: This is the JAR file for TeSSLa.
- A Home Assistant installation.

**Before Installation:**

- Make sure you have a working installation of Home Assistant, either on a physical device or in a container.
- Ensure that you have Java installed on your system. TeSSLa Interpreter requires Java to run.
- Download the TeSSLa Interpreter JAR file from tessla.io.

**Installation:**

1. Download the project files for TeSSLa integration.
2. Rename the TeSSLa Interpreter file to `tessla.jar`.
3. Place `tessla.jar` in the same folder as the rest of the project files.
4. Copy the entire TeSSLa integration folder into the `components` folder in your Home Assistant system.

**Usage:**

1. Open the Home Assistant interface and go to **Settings**.
2. Select **Integrations** from the menu.
3. Click on **Add Integrations** and search for **TeSSLa**.
4. When the TeSSLa integration appears in the search results, click on it.
5. You will be presented with the TeSSLa integration dialog.
