# World Generation and Geography Data

This directory contains data files for Visual DM's world generation, regions, and Points of Interest (POIs).

## Directory Structure

- `regions/`: Region definitions, metadata, and geographic properties
- `pois/`: Point of Interest data, including cities, dungeons, and landmarks
- `generation/`: World generation parameters, algorithms, and seed data

## POI Density Guidelines

According to the Development Bible:

- Each region contains approximately 20 major POIs (towns, dungeons, etc.)
- Each region includes 200-400 minor/nature squares (groves, ruins, camps, etc.)
- The remainder of the region consists of wilderness or terrain hexes

## Usage

These data files are consumed by the world generation and region management systems. They define the structure, geography, and content of the game world.

For detailed implementation information, see the World Generation and Region System documentation in the Development Bible. 