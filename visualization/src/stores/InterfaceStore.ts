import { atom } from "recoil";

export const mapViewport = atom<Record<string, any>>({
  key: "mapview",
  default: {
    latitude: 52.503797177988844,
    longitude: 13.299512588353677,
    zoom: 8.696205280855345
  },
  dangerouslyAllowMutability: true
})

export const selectedGroupAtom = atom<number | null>({
  key: "selectedGroup",
  default: null
})
