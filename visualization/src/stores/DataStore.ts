import { selector } from "recoil";
import { selectedGroupAtom } from "./InterfaceStore";
import bbox from '@turf/bbox'


export const convexHullSelector = selector({
  key: "convexHulls",
  get: async () => {
    return await fetch("/data/groupRegions.geojson").then(resp => resp.json())
  }
})

export const usersSelector = selector({
  key: "users",
  get: async () => {
    return await fetch("/data/usersAssignments.geojson").then(resp => resp.json())
  }
})

export const meetingPointsSelector = selector({
  key: "meetinPoints",
  get: async () => {
    return await fetch("/data/groupMeetingPoints.geojson").then(resp => resp.json())
  }
})

export const boundsSelector = selector<[[number, number], [number, number]]>({
  key: "bounds",
  get: async ({ get }) => {
    let users = get(usersSelector)
    return bbox(users)
    // let bounds = users.features.reduce((bounds: [number, number, number, number], feature: any) => {
    //   const coords = feature.geometry.coordinates
    //   return [
    //     Math.min(bounds[0], coords[0]),
    //     Math.max(bounds[1], coords[0]),
    //     Math.min(bounds[2], coords[1]),
    //     Math.max(bounds[3], coords[1]),
    //   ]
    // }, [180, -180, 90, -90])
    // return [[bounds[0], bounds[2]], [bounds[1], bounds[3]]]
  }
})

export const groupIdsSelector = selector<number[]>({
  key: "groupIds",
  get: ({ get }) => {
    const meetingPoints = get(meetingPointsSelector)
    return meetingPoints.features.map((mp: any) => mp.properties.label)
  }
})

export const maxMinLabelsSelector = selector<[number, number]>({
  key: "maxMinLabels",
  get: ({ get }) => {
    const groupIds = get(groupIdsSelector)
    return [Math.min(...groupIds), Math.max(...groupIds)]
  }
})


export const selectedGroupDetailsSelector = selector({
  key: 'selectedGroupDetails',
  get: ({ get }) => {
    const selectedGroupId = get(selectedGroupAtom)
    const groups = get(convexHullSelector)
    const users = get(usersSelector)
    const meetingPoints = get(meetingPointsSelector)

    if (selectedGroupId === null) return null
    const selectedGroup = groups.features.find((f: any) => f.properties.label === selectedGroupId)
    const selectedUsers = users.features.filter((f: any) => f.properties.label === selectedGroupId)
    const selectedMeetingPoint = meetingPoints.features.find((f: any) => f.properties.label === selectedGroupId)
    return {
      users: selectedUsers.map((u: any) => u.properties),
      selectedGroup: selectedGroup.properties,
      selectedMeetingPoint: selectedMeetingPoint.properties,
      bounds: bbox(selectedGroup)
    }
  }
})

