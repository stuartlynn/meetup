import { selector } from "recoil";
import { selectedGroupAtom } from "./InterfaceStore";
//@ts-ignore
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

export const clusterSizesSelector = selector({
  key: "clusterSizesSelector",
  get: ({ get }) => {
    let users = get(usersSelector)
    return users.features.reduce((counts: Record<number, number>, user: any) => {
      let label = user.properties.label
      counts[label] = label in counts ? counts[label] + 1 : 1
      return counts
    }, {})
  }
})


export const runDetailsSelector = selector({
  key: "runDetails",
  get: async () => {
    return await fetch("/data/runDetails.json").then(resp => resp.json())
  }
})

export const boundsSelector = selector<[[number, number], [number, number]]>({
  key: "bounds",
  get: async ({ get }) => {
    let users = get(usersSelector)
    return bbox(users)
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

