from typing import Set, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem


def is_all_checked(list_widget: QListWidget) -> bool:
    for i in range(list_widget.count()):
        item: QListWidgetItem = list_widget.item(i)
        if item.checkState() == Qt.Unchecked:
            return False
    return True


def check_all(list_widget: QListWidget) -> None:
    check_state = Qt.Checked

    if is_all_checked(list_widget):
        check_state = Qt.Unchecked

    for i in range(list_widget.count()):
        item: QListWidgetItem = list_widget.item(i)
        item.setCheckState(check_state)


def delete_from_list(list_widget: QListWidget) -> Set[str]:
    checked_items = get_checked_items(list_widget)

    deleted_items = set()
    for item in checked_items:
        deleted_items.add(item.text().strip())
        row = list_widget.row(item)
        list_widget.takeItem(row)

    return deleted_items


def get_checked_items(list_widget: QListWidget) -> List[QListWidgetItem]:
    checked_items = []
    for i in range(list_widget.count()):
        item: QListWidgetItem = list_widget.item(i)
        if item.checkState() == Qt.Checked:
            checked_items.append(item)
    return checked_items
