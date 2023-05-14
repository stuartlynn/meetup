import { useRecoilValue } from 'recoil';
import React from 'react'
//@ts-ignore
import { Histogram, DensitySeries, BarSeries, withParentSize, XAxis, YAxis } from '@data-ui/histogram';
import { clusterSizesSelector } from '../stores/DataStore';

export const ClusterSizeHistogram: React.FC = () => {
  const clusterSizes = useRecoilValue(clusterSizesSelector)


  return (
    <Histogram
      width={400}
      height={300}
      ariaLabel="Group Size Distrobution"
      orientation="vertical"
      cumulative={false}
      normalized={true}
      binCount={25}
      valueAccessor={(datum: any) => datum}
      binType="numeric"
    //@ts-ignore
    >
      <BarSeries
        animated
        rawData={Object.values(clusterSizes)}
      />
      <XAxis />
      <YAxis />
    </Histogram>
  )
}
