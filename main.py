import sys
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QMessageBox

# Модель данных нашей таблицы
class TableModel(QtCore.QAbstractTableModel):
    # Конструктор нашей модели
    def __init__(self, data):
        super(TableModel, self).__init__()
        # В _data записывается DataFrame из Pandas
        self._data = data

    # Эта функция отвечает за вывод информации в таблицу в виде строки
    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    # Эта функция позволяет узнать кол-во строк
    def rowCount(self, index):
        return self._data.shape[0]

    # Эта функция позволяет узнать кол-во столбцов
    def columnCount(self, index):
        return self._data.shape[1]

    # Эта функция отвечает за описание индексов и название столбцов в таблице соответственно
    def headerData(self, section, orientation, role):
        if role in [Qt.DisplayRole, Qt.EditRole]:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            if orientation == Qt.Vertical:
                return str(self._data.index[section])

    # Эта функция даёт нам возможность взаимодействовать с ячейками таблицы
    def flags(self, index):
        if index.column() >= 1:
            return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    # Эта функция даёт нам возможность изменять информацию, а после сохранять её
    def setData(self, index, value, role):
        self._data.iloc[index.row(), index.column()] = value
        print(self._data)
        self._data.to_csv('info.csv', encoding='utf-8', index=False)
        return super(TableModel, self).setData(index, value, role)

# Класс делегата, который позволяет редактировать в таблице информацию
class DelegateForTableAdditing(QStyledItemDelegate):
    def __init__(self):
        super().__init__()

    # Позволяет создать на выбранной ячейки для редактирования поле для записи информации
    def createEditor(self, parent, option, index):
        if index.column() >= 1:
            return super(DelegateForTableAdditing, self).createEditor(parent, option, index)
        else:
            return None

    # Позволяет в поле для редактирования задать текст, который был до этого в ячейке
    def setEditorData(self, editor, index):
        if index.column() >= 1:
            text = index.data(Qt.EditRole) or index.data(Qt.DisplayRole)
            editor.setText(text)


# Делегат, который позволяет вставлять в нашу таблицу кнопки
# После вставки кнопки мы сможем с ней работать
class PushButtonDelegate(QStyledItemDelegate):
    clicked = QtCore.pyqtSignal(QtCore.QModelIndex)

    # Позволяет понять, где в таблице надо втравлять кнопки
    def paint(self, painter, option, index):
        if (
            isinstance(self.parent(), QtWidgets.QAbstractItemView)
            and self.parent().model() is index.model()
        ):
            self.parent().openPersistentEditor(index)

    # Функция создаёт нашу кнопку с которой можно будет потом работать
    def createEditor(self, parent, option, index):
        button = QtWidgets.QPushButton(parent)
        button.clicked.connect(lambda *args, ix=index: self.clicked.emit(ix))
        return button

    # Позволяет задать название для нашей кнопки
    def setEditorData(self, editor, index):
        editor.setText(f"Строка {index.row()}")

    def setModelData(self, editor, model, index):
        pass


class MainWindow(QtWidgets.QMainWindow):

    # Конструктор нашего окна
    def __init__(self):
        super().__init__()
        self.resize(880, 400)

        # Создаём контейнер в котором будут находиться все элементы
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.resize(880, 400)

        # Добавляем кнопку добавления новой строки
        self.btn_add_row = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_row.resize(200, 40)
        self.btn_add_row.move(665, 300)
        self.btn_add_row.setText("Добавить новую строку")
        self.btn_add_row.pressed.connect(self.add_row)

        # Добавляем кнопку добавления новой колонки
        self.btn_add_col = QtWidgets.QPushButton(self.centralwidget)
        self.btn_add_col.resize(200, 40)
        self.btn_add_col.move(665, 250)
        self.btn_add_col.setText("Добавить новый столбец")
        self.btn_add_col.pressed.connect(self.add_col)

        # Добавляем текстовое окно, текст из которой передадим в название колонки
        self.text_for_col = QtWidgets.QTextEdit(self.centralwidget)
        self.text_for_col.resize(200, 40)
        self.text_for_col.move(665, 200)
        self.text_for_col.setText("Нов. Столбец")

        # Добавляем кнопку удаление строки
        self.btn_delete_row = QtWidgets.QPushButton(self.centralwidget)
        self.btn_delete_row.resize(200, 40)
        self.btn_delete_row.move(665, 90)
        self.btn_delete_row.setText("Удалить выбранную строку")
        self.btn_delete_row.pressed.connect(self.delete_row)

        # Добавляем кнопку удаление столбца
        self.btn_delete_col = QtWidgets.QPushButton(self.centralwidget)
        self.btn_delete_col.resize(200, 40)
        self.btn_delete_col.move(665, 40)
        self.btn_delete_col.setText("Удалить выбранный столбец")
        self.btn_delete_col.pressed.connect(self.delete_col)

        # Создаём объект таблицы в котором будет храниться информация
        self.table = QtWidgets.QTableView(self.centralwidget)
        self.table.resize(645, 400)

        # Считываем информацию из csv файла в DataFrame
        data = pd.read_csv('info.csv', delimiter=',')

        # Создаём объект модель нашей таблицы
        self.model = TableModel(data)
        # После чего устанавливаем её, как модель таблицы
        self.table.setModel(self.model)
        # К View нашей таблицы прикручиваем функцию,
        # Которая будет выводить информацию о выбранной строчке в Debug
        self.table.selectionModel().selectionChanged.connect(self.see_row_info_in_debug)

        # Создаём делегат, который создаст в нашем View кнопки в первой колонке,
        # По которым мы сможем смотреть информацию из Model о строчке из таблицы
        delegate = PushButtonDelegate(self.table)
        self.table.setItemDelegateForColumn(0, delegate)
        delegate.clicked.connect(self.create_messagebox_of_row_information)

        # Добавляем делегат для изменения информации в таблице
        self.delegate1 = DelegateForTableAdditing()
        self.table.setItemDelegate(self.delegate1)

    def create_messagebox_of_row_information(self, index):
        # Создаём окошко
        msg = QMessageBox()
        msg.setWindowTitle(f"Индекс {index.row()}")
        # Обрабатываем нашу информацию, чтобы записать её в виде текста
        val = list(self.model._data.iloc[index.row()].values)
        ind = list(self.model._data.iloc[index.row()].index)
        info = [f"{ind[i]} = {val[i]}" for i in range(1, len(val))]
        info = "\n".join(info)
        # Создаём окошко
        msg.setText(info)
        msg.exec_()

    def see_row_info_in_debug(self, selected, deselected):
        # Выводим в виде Series информацию о строке
        for i in selected.indexes():
            print(self.model._data.iloc[i.row(), 1:], end='\n\n')
        pass

    def add_row(self):
        # Создаём новую строку, которая будет заполнена NaN
        self.model._data.loc[len(self.model._data)] = np.nan
        self.model.layoutChanged.emit()
        self.save()

    def add_col(self):
        # Создаёи колонку с NaN значениями
        self.model._data.loc[:, self.text_for_col.toPlainText()] = np.nan
        self.model.layoutChanged.emit()
        self.save()

    def delete_row(self):
        # Получаем выделенные элементы таблицы
        indexes = self.table.selectedIndexes()
        if indexes:
            # После чего выбираем первый выбранный элемент
            index = indexes[0]
            # После удаляем строчку и обновляем индексы DataFrame
            self.model._data = self.model._data.drop(index=[index.row()], axis=0)
            self.model._data = self.model._data.reset_index(drop=True)
            self.model.layoutChanged.emit()
            self.table.clearSelection()
            self.save()

    def delete_col(self):
        # Получаем выделенные элементы таблицы
        indexes = self.table.selectedIndexes()
        if indexes:
            # После чего выбираем первый выбранный элемент
            index = indexes[0]
            # Если он является колонкой с кнопками, то её мы не сможем удалить
            if(index.column() == 0):
                print("Невозможно удалить кнопки показа информации")
                return()
            # А после удаляем столбец из DataFrame
            self.model._data = self.model._data.drop(self.model._data.columns[[index.column()]], axis=1)
            self.model.layoutChanged.emit()
            self.table.clearSelection()
            self.save()

    def save(self):
        # После каждого изменения в таблице и изменения её структуры мы должны записать информацию в csv
        self.model._data.to_csv('info.csv', encoding='utf-8', index=False)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    window = MainWindow()
    window.show()
    app.exec_()