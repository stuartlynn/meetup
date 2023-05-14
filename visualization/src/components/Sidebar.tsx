import React from 'react'
import { ComboBox, Flex, Item, ActionButton, Text, Header } from '@adobe/react-spectrum'
import { GroupsViewer } from './GroupsViewer'
import { SelectedGroupInfo } from './SelectedGroupInfo'
import { useRecoilState, useRecoilValue } from 'recoil'
import { selectedGroupAtom } from '../stores/InterfaceStore'
import { groupIdsSelector } from '../stores/DataStore'


export const Sidebar: React.FC = () => {
  const groupIds = useRecoilValue(groupIdsSelector)
  const [selectedGroupId, setSelectedGroupId] = useRecoilState(selectedGroupAtom)

  const groupItems = groupIds.map(g => ({ id: `${g}`, name: `${g}` }))
  return (
    <div style={{ width: "250px", height: "95vh", top: "2.5vh", right: "20px", position: 'absolute', zIndex: 1, backgroundColor: "white", boxSizing: "border-box", padding: "10px", boxShadow: "1px 1px 26px 2px rgba(0,0,0,0.75)" }}>
      <Flex direction="column">
        {selectedGroupId !== null &&

          <Header>
            <Flex direction={"row"} justifyContent={"space-between"} alignItems={"center"}>
              <Text>Selected Group : {selectedGroupId}</Text>
              <ActionButton onPress={() => setSelectedGroupId(null)}> Clear</ActionButton>
            </Flex>
          </Header>

        }

        <ComboBox width="100%" label={"Group"} defaultItems={groupItems} selectedKey={selectedGroupId} onSelectionChange={(newKey) => setSelectedGroupId(parseInt(newKey as string))}>
          {item => <Item key={item.id}>{item.name}</Item>}
        </ComboBox>
        <GroupsViewer />
        <SelectedGroupInfo />
      </Flex>
    </div>
  )
}
