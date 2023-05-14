import { atom } from "recoil";

export const mapViewport = atom({
  key: "mapview",
  default: {
    latitude: 0,
    longitude: 0,
    zoom: 0
  },
  dangerouslyAllowMutability: true
})

export const selectedGroupAtom = atom<number | null>({
  key: "selectedGroup",
  default: null
})
