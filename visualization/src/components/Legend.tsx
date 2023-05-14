import React from 'react'
import { Flex, Heading, Text } from '@adobe/react-spectrum'
import { colors } from '../utils/colors'

const Circle: React.FC<{ size: number, color: Array<number> }> = ({ size, color }) => {
  return (
    <span style={{
      height: `${size}px`,
      width: `${size}px`,
      backgroundColor: `rgb(${color.join(",")})`,
      borderRadius: "50%",
      display: "inline-block"
    }} />
  )
}

const Line: React.FC<{ size: number, color: Array<number> }> = ({ size, color }) => {
  return (
    <span style={{
      height: `5px`,
      width: `${size}px`,
      backgroundColor: `rgb(${color.join(",")})`,
      borderRadius: "5px",
      display: "inline-block"
    }} />
  )
}

export const Legend: React.FC = () => {
  return (
    <div className="overlay"
      style={{
        width: "200px",
        height: "150px",
        bottom: "2.5vh",
        right: "20px"
      }}>
      <Flex direction="column" gap="size-100">
        <Heading>Legend</Heading>
        <Flex direction="row" justifyContent={"space-between"} alignItems={'center'}>
          <Circle size={25} color={colors.user} />
          <Text>User</Text>
        </Flex>
        <Flex direction="row" justifyContent={"space-between"} alignItems={'center'}>
          <Circle size={25} color={colors.meetingPoint} />
          <Text>Meeting Point</Text>
        </Flex>
        <Flex direction="row" justifyContent={"space-between"} alignItems={'center'}>
          <Line size={25} color={colors.groupBoundary} />
          <Text>Group Region</Text>
        </Flex>
      </Flex>
    </div>
  )
}
