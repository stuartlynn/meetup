import React from 'react'
import { ComboBox, Flex, Item, ActionButton, Text, Heading, Divider } from '@adobe/react-spectrum'
import { SelectedGroupInfo } from './SelectedGroupInfo'
import { useRecoilState, useRecoilValue } from 'recoil'
import { selectedGroupAtom } from '../stores/InterfaceStore'
import { groupIdsSelector } from '../stores/DataStore'
import { RunDetails } from './RunDetails'
import { ClusterSizeHistogram } from './ClusterSizeHistogram'


export const Sidebar: React.FC = () => {
  const groupIds = useRecoilValue(groupIdsSelector)
  const [selectedGroupId, setSelectedGroupId] = useRecoilState(selectedGroupAtom)

  const groupItems = groupIds.map(g => ({ id: `${g}`, name: `${g}` }))
  return (
    <div style={{ width: "400px", height: "95vh", top: "2.5vh", left: "20px", position: 'absolute', zIndex: 1, backgroundColor: "white", boxSizing: "border-box", padding: "10px", boxShadow: "1px 1px 26px 2px rgba(0,0,0,0.75)" }}>
      <Flex direction="column" gap="size-200">
        <RunDetails />
        <Divider size="M" orientation='horizontal' />

        <Heading>
          {selectedGroupId !== null ?
            <Flex direction={"row"} justifyContent={"space-between"} alignItems={"center"}>
              <Text>Selected Group : {selectedGroupId}</Text>
              <ActionButton onPress={() => setSelectedGroupId(null)}> Clear</ActionButton>
            </Flex>
            :
            <Text>Select a group to see occupancy</Text>

          }
        </Heading>

        <ComboBox width="90%" label={"Select a group to view"} defaultItems={groupItems} selectedKey={selectedGroupId} onSelectionChange={(newKey) => setSelectedGroupId(parseInt(newKey as string))}>
          {item => <Item key={item.id}>{item.name}</Item>}
        </ComboBox>
        <SelectedGroupInfo />

        <Divider size="M" orientation='horizontal' />
        <Heading>Cluster Sizes</Heading>
        <ClusterSizeHistogram />
      </Flex>
    </div>
  )
}
