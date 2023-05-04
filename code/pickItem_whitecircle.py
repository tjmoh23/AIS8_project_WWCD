# df_mat은 2023년 4월 27일부터 4월 29일까지의 글로벌 매치 목록 정보
# 해당 매치에서 선수들의 아이템 픽업 위치와 자기장(whitecircle) 지도 시각화 함수 만들기

def white_pick_map(number):
    
    def find_pick_item(number):
        # telemetry JSON 데이터 가져오기
        telemetry_url = df_mat['telemetry_url'][number]
        rs_tele_event = requests.get(telemetry_url, headers=header)
        telemetry_json = rs_tele_event.json()

        # 데이터프레임으로 보기
        df_telemetry_data = pd.DataFrame(telemetry_json)
        df_ItemPickup = df_telemetry_data[(df_telemetry_data["_T"]=="LogItemPickup")
                        |(df_telemetry_data["_T"]=="LogItemPickupFromVehicleTrunk")|(df_telemetry_data["_T"]=="LogItemPickupFromCarepackage")]

        # 아이템 픽업 로그에서 필요한 컬럼만 추출하기
        df_ItemPickup = df_ItemPickup[["_D", "character", "item"]]
        df_ItemPickup = df_ItemPickup.reset_index()
        df_ItemPickup = df_ItemPickup.drop("index", axis=1)

        # character 컬럼 뜯어서 데이터프레임 만들기
        character = pd.DataFrame()
        for i in range(0, len(df_ItemPickup)):
            pic = pd.DataFrame([df_ItemPickup["character"][i].values()])
            character = pd.concat([character, pic], ignore_index=True)

        character.columns = ['name', 'teamId', 'health', 'location', 'ranking', 'individualRanking', 'accountId', 'isInBlueZone', 'isInRedZone', 'zone']
        # 다 0인 컬럼 제거
        character = character.drop(["ranking", "individualRanking"], axis=1)
        location = pd.DataFrame()
        for i in range(0, len(df_ItemPickup)):
            loc = pd.DataFrame([character["location"][i].values()])
            location = pd.concat([location, loc], ignore_index=True)
        location.columns = [['x', 'y', 'z']]

        # 두 개의 데이터프레임 합치기
        df_pick = pd.concat([character, location], axis=1)
        df_pick = df_pick.drop("location", axis=1)

        # item 컬럼 뜯어서 데이터프레임 만들기
        item = pd.DataFrame()
        for i in range(0, len(df_ItemPickup)):
            sample = pd.DataFrame([df_ItemPickup["item"][i].values()])
            item = pd.concat([item, sample], ignore_index=True)

        item.columns = ['itemId', 'stackCount', 'category', 'subCategory', 'attachedItems']

        # 빈값 컬럼 제거
        # 최종 데이터프레임 합치기
        item = item.drop("attachedItems", axis=1)
        df_pick_item = pd.concat([df_pick, item], axis=1)

        df_pick_item = pd.concat([df_ItemPickup, df_pick_item], axis=1) # 가장 처음 데이터프레임과 합치기
        df_pick_item = df_pick_item.drop(["character", "item"], axis=1)

        return df_pick_item

    # 매치number에 해당하는 데이터프레임 불러오는 함수
    find_pick_item = find_pick_item(number)

    # 화이트써클  
    match_id = df_mat["id"][number]
    match = pubg.match(match_id)
    url = df_mat["telemetry_url"][number]
    telemetry = pubg.telemetry(url)
    events = telemetry.events

    # Desert_Main/Baltic_Main (819200, 819200)
    map_id = telemetry.map_id()
    mapx, mapy = map_dimensions[map_id]

    circles = telemetry.circle_positions()
    whites = np.array(circles['white'])
    whites[:, 2] = mapy - whites[:, 2]
    phases = np.where(whites[1:, 4] - whites[:-1, 4] != 0)[0] + 1

    fig = plt.figure(figsize=(10, 10), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")

    # 이미지 설정
    if map_id == 'Desert_Main':
        img_path = '/content/Miramar_Main_Low_Res.png'
        img = mpimg.imread(img_path)
    else:
        img_path = '/content/Erangel_Main_Low_Res.png'
        img = mpimg.imread(img_path)

    ax.imshow(img, extent=[0, mapx, 0, mapy])
    for phase in phases:
            white_circle = plt.Circle((whites[phase][1], whites[phase][2]), whites[phase][4],
                                    edgecolor="w", linewidth=1.1, fill=False, zorder=5)
            ax.add_patch(white_circle)

    # 좌표를 밀도 분포로 변환하여 출력
    ax.imshow(img, extent=[0, mapx, 0, mapy])
    xy = np.vstack([find_pick_item[('x',)], mapy - find_pick_item[('y',)]])
    z = gaussian_kde(xy)(xy)
    ax.scatter(find_pick_item[('x',)], mapy - find_pick_item[('y',)], marker="o", c=z, edgecolor="k", s=45, linewidths=0.8, zorder=20)

    return plt.savefig(f"match{number}_white_pick.png")
  
# plt.savefig("파일명"): 파일 저장
# plt.show와 함께 쓸 수 없다
