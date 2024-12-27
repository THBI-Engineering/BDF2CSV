# 20240705_day5_teaching_experiment [Alignment of EEG and Audio]

Author: 沈逸潇 fusedbuzzer@gmail.com

Date: 27/12/2024


## 项目目录结构
```
.
├── README.md
├── requirements.txt
├── makefile                run main.py
├── main.py                 bdf2csv, like data.csv & evt.csv
├── alignment.py            Allignment of EEG(ESG, SPO2, e.t.c.) and Audio(.wav)
├── song_synthesis.py       按顺序合成歌曲，以此查看与当天录制的是否相同顺序
```


# 数据对齐
## 使用最后一个触发标(TriggerNum=9)对齐音频(.wav)和数据(EEG+SPO2+GSR+ECG+...)

### 1. 对齐逻辑
1. 主机程序打标发送记录, ```trigger_201_to_1705_20240705-111433_sync.txt```: 
    1. 一共发了1505个"9"
    2. 最后一个发出去的"9": ```1705, 9, 1720149272575745600```

2. 主机声卡打标接收记录, ```recording_20240705-111440_sync.txt```:
    1. 因为前面部分没有录上，所以实际声卡录音只收了1478个"9"
    2. 最后一个接收到的"9": ```9, 70896480, 1720149272602526200```---> 对应到音频的70896480/480*10ms=1477.01s

3. 博睿康打标接收记录, ```EEG_BRKs/evt.csv```
    1. 博睿康收到了1505个"9"，与主机发出去的数量一致
    2. 最后一个发出去的"9": ```1839.350,0.0,9, ```

### 2. Add music_pos column into evt.csv
只匹配"主机声卡打标接收记录"&"博睿康打标接受记录"--->```在evt.csv中timeindex=1839.350(second)那行，写入{'music_pos': 1477.01s}。然后从后往前，重复该操作```

### 3. Add song_idx column into evt.csv
通过音频波形，手动确认每首歌曲的开始时间和结束时间，以及歌曲index，得到song_pos和song_list。最后写入evt-aligned.csv