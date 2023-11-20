import os
import json


class DetectArgorithm:

    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.unique_id_coordinates = dict()
        self.data = dict()
        self.enter_coordinates = list()
        self.exit_coordinates = list()

    def load_file(self) -> None:
        with open(os.path.dirname(os.path.abspath(__file__))
                  + self.file_name) as detections_file:
            self.data = json.load(detections_file)

    def read_file(self) -> None:
        print(json.dumps(self.data, indent=4))

    def fill_enter_coordinates(self) -> None:
        self.enter_coordinates = self.data["eventSpecific"]["nnDetect"]["10_8_3_203_rtsp_camera_3"]["cfg"]["cross_lines"][0]["int_line"]

    def fill_exit_coordinates(self) -> None:
        self.exit_coordinates = self.data["eventSpecific"]["nnDetect"]["10_8_3_203_rtsp_camera_3"]["cfg"]["cross_lines"][0]["ext_line"]

    def fill_unique_track_id(self) -> None:
        """
        Функция заполняет словарь, в котором ключи - это уникальные track_id,
        а значения - список передвижений координат центральной точки детекции
        """
        frames_data = self.data["eventSpecific"]["nnDetect"]["10_8_3_203_rtsp_camera_3"]["frames"]
        for frame in frames_data.values():
            person_data = frame["detected"]["person"]

            for person in person_data:
                if len(person) > 5:
                    person_coordinates = person[0:4]
                    person_id = person[5]
                    center_point = round((person_coordinates[0] + person_coordinates[2]) / 2), round((person_coordinates[1] + person_coordinates[3]) / 2)
                    # center_point - это использования формулы
                    # медиан для поиска координат центральной точки
                    # детекции и округление их
                    for track in person_id.values():
                        if track["track_id"] in self.unique_id_coordinates.keys():
                            self.unique_id_coordinates[track["track_id"]].append(center_point)
                        else:
                            self.unique_id_coordinates[track["track_id"]] = [center_point]

    def generate_count_unique_id_coordinates(self) -> int:
        """
        Функция возвращает количества уникальных track_id, у которых
        есть хотя бы одно передвижение центральной точки детекции
        """
        count = 0
        for i in self.unique_id_coordinates.items():
            if len(i[1]) > 1:
                count += 1
        return count

    def generate_enters_count(self) -> int:
        """
        Функция подсчитыват количество пересечений отрезков
        движения детекций с отрезком входа
        """
        bx1 = self.enter_coordinates[0]
        by1 = self.enter_coordinates[1]
        bx2 = self.enter_coordinates[2]
        by2 = self.enter_coordinates[3]
        count = 0
        for uniq in self.unique_id_coordinates.values():
            if len(uniq) > 1:
                for i in range(len(uniq)):
                    ax1 = uniq[i][0]
                    ay1 = uniq[i][1]
                    ax2 = uniq[i-1][0]
                    ay2 = uniq[i-1][1]
                    v1 = (bx2 - bx1) * (ay1 - by1) - (by2 - by1) * (ax1 - bx1)
                    v2 = (bx2 - bx1) * (ay2 - by1) - (by2 - by1) * (ax2 - bx1)
                    v3 = (ax2 - ax1) * (by1 - ay1) - (ay2 - ay1) * (bx1 - ax1)
                    v4 = (ax2 - ax1) * (by2 - ay1) - (ay2 - ay1) * (bx2 - ax1)
                    if v1*v2 < 0 and v3*v4 < 0:
                        count += 1
        return count

    def generate_exits_count(self) -> int:
        """
        Функция подсчитыват количество пересечений отрезков
        движения детекций с отрезком выхода
        """
        zx1 = self.exit_coordinates[0]
        zy1 = self.exit_coordinates[1]
        zx2 = self.exit_coordinates[2]
        zy2 = self.exit_coordinates[3]
        count = 0
        for uniq in self.unique_id_coordinates.values():
            if len(uniq) > 1:
                for i in range(len(uniq)):
                    ax1 = uniq[i][0]
                    ay1 = uniq[i][1]
                    ax2 = uniq[i-1][0]
                    ay2 = uniq[i-1][1]
                    v1 = (zx2 - zx1) * (ay1 - zy1) - (zy2 - zy1) * (ax1 - zx1)
                    v2 = (zx2 - zx1) * (ay2 - zy1) - (zy2 - zy1) * (ax2 - zx1)
                    v3 = (ax2 - ax1) * (zy1 - ay1) - (ay2 - ay1) * (zx1 - ax1)
                    v4 = (ax2 - ax1) * (zy2 - ay1) - (ay2 - ay1) * (zx2 - ax1)
                    if v1*v2 < 0 and v3*v4 < 0:
                        count += 1
        return count


def main():
    algorithm = DetectArgorithm('/detections.json')
    algorithm.load_file()
    algorithm.fill_enter_coordinates()
    algorithm.fill_exit_coordinates()
    algorithm.fill_unique_track_id()
    print(algorithm.generate_enters_count())
    print(algorithm.generate_exits_count())
    print(algorithm.generate_count_unique_id_coordinates())


if __name__ == "__main__":
    main()
