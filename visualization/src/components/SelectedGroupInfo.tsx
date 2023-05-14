
import React from 'react'
import { selectedGroupDetailsSelector } from '../stores/DataStore'
import { useRecoilValue } from 'recoil'
import { ListBox, Item, Header } from '@adobe/react-spectrum'

export const SelectedGroupInfo: React.FC = () => {
  const selectedGroupDetails = useRecoilValue(selectedGroupDetailsSelector)
  if (selectedGroupDetails === null) return null
  const userItems = selectedGroupDetails.users.map((u: any) => ({ id: u.user_id, label: u.user_id }))
  return (
    <div>
      <Header>Group has {selectedGroupDetails.users.length} Users</Header>
      <div style={{ height: "200px", overflowY: "auto" }}>
        <ListBox>
          {userItems.map((item: any) =>
            //@ts-ignore
            <Item id={item.id}>{item.label}</Item>
          )}
        </ListBox>
      </div>
    </div >
  )
}
