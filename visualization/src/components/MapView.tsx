import React, { useEffect } from 'react'
import { Map, NavigationControl } from 'react-map-gl'
import { DeckGL, FlyToInterpolator, GeoJsonLayer, WebMercatorViewport } from "deck.gl/typed"
import { DataFilterExtension } from '@deck.gl/extensions/typed';
import 'maplibre-gl/dist/maplibre-gl.css';

import maplibregl from 'maplibre-gl';
import { boundsSelector, convexHullSelector, maxMinLabelsSelector, meetingPointsSelector, selectedGroupDetailsSelector, usersSelector } from '../stores/DataStore';
import { mapViewport, selectedGroupAtom } from '../stores/InterfaceStore';
import { useRecoilValue, useRecoilState } from 'recoil';
import { colors } from '../utils/colors'

export const MapView: React.FC = () => {
  const convexHulls = useRecoilValue(convexHullSelector)
  const users = useRecoilValue(usersSelector)
  const meetingPlaces = useRecoilValue(meetingPointsSelector)
  const [selectedGroup, setSelectedGroup] = useRecoilState(selectedGroupAtom)
  const selectedGroupDetails = useRecoilValue(selectedGroupDetailsSelector)

  const dataSetBounds = useRecoilValue(boundsSelector)
  const [mapView, setMapView] = useRecoilState(mapViewport)
  const minMaxLabels = useRecoilValue(maxMinLabelsSelector)

  const convexHullLayer = new GeoJsonLayer({
    id: "hulls",
    data: convexHulls,
    getFillColor: [0, 0, 0, 0],
    getLineColor: colors.groupBoundary,
    getLineWidth: 4,
    lineWidthUnits: "pixels",
    getFilterValue: (f: any) => f.properties.label,
    filterRange: selectedGroup ? [selectedGroup - 0.1, selectedGroup + 0.1] : minMaxLabels,
    extensions: [new DataFilterExtension({ filterSize: 1 })],
    pickable: true,
    onClick: (info) => {
      console.log("Click info is", info)
      setSelectedGroup(info.object.properties.label)
    }
  })

  const userLayer = new GeoJsonLayer({
    id: "users",
    data: users,
    getRadius: 50,
    getFillColor: colors.user,
    pointRadiusUnits: "meters",
    getFilterValue: (f: any) => f.properties.label,
    filterRange: selectedGroup ? [selectedGroup - 0.1, selectedGroup + 0.1] : minMaxLabels,
    extensions: [new DataFilterExtension({ filterSize: 1 })],
  })

  const meetingPointLayer = new GeoJsonLayer({
    id: "users",
    data: meetingPlaces,
    getRadius: 50,
    getFillColor: colors.meetingPoint,
    pointRadiusUnits: "meters",
    getFilterValue: (f: any) => f.properties.label,
    filterRange: selectedGroup ? [selectedGroup - 0.1, selectedGroup + 0.1] : minMaxLabels,
    extensions: [new DataFilterExtension({ filterSize: 1 })],
  })

  useEffect(() => {
    setTimeout(() => {
      if (mapView.width && mapView.height) {
        let boundsToUse = selectedGroupDetails !== null ? selectedGroupDetails.bounds : dataSetBounds
        let viewport = new WebMercatorViewport(mapView);
        let newViewport = viewport.fitBounds([[boundsToUse[0], boundsToUse[1]], [boundsToUse[2], boundsToUse[3]]], { padding: 200 })

        setMapView({
          ...newViewport,
          transitionDuration: 1000,
          transitionInterpolator: new FlyToInterpolator()
        })
      }
    }, 10)
  }, [selectedGroupDetails, dataSetBounds])

  // This is requied as deckgl tries to modify the value of viewport mutably interally 
  // recoil doesn't like this 
  let localViewport = { ...mapView }

  return (
    <DeckGL
      layers={[convexHullLayer, userLayer, meetingPointLayer]}
      initialViewState={localViewport}
      onViewStateChange={({ viewState }) => {
        setMapView(viewState)
      }}
      style={{ width: "100%", height: "100%" }}
      controller={true}
    >
      <Map
        mapLib={maplibregl}
        mapStyle={"https://api.maptiler.com/maps/topo-v2/style.json?key=32rtUQVfWVrA5316PfSR"}
      >
        <NavigationControl position="top-left" />
      </Map>
    </DeckGL>
  )
} 
