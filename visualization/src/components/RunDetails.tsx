import React from 'react'
import { useRecoilValue } from 'recoil'
import { runDetailsSelector } from '../stores/DataStore'
import { View, Heading, Text, Flex } from "@adobe/react-spectrum"

export const RunDetails: React.FC = () => {
  const runDetails = useRecoilValue(runDetailsSelector)

  return (
    <View>
      <Heading>Run: {runDetails.name}</Heading>
      <Flex direction="row" justifyContent={"space-between"}><Text>Target Min Cluster Size</Text> {runDetails.minOccupancy ?? "None"}</Flex>
      <Flex direction="row" justifyContent={"space-between"}><Text>Target Max Cluster Size </Text>{runDetails.maxOccupancy ?? "None"}</Flex>
      <Flex direction="row" justifyContent={"space-between"}><Text>Max iterations </Text>{runDetails.maxIters ?? "10"}</Flex>
      <Flex direction="row" justifyContent={"space-between"}><Text>Strategy  </Text>{runDetails.meetingPointMethod}</Flex>
    </View>
  )
}
