import os
import shutil
import sys
from datetime import datetime

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
import lucidity as lc

BASE_SHOW_URL = "D:\\Projects\\REDESIGN"
template = lc.Template('SAM_Template',
                       "{OUTPUT_DIR}" +
                       '\\{PROJECTNAME}\\{DATE}\\{PROJECTNAME}_{SHOTNAME}\\{TASKNAME}\\{EXT}\\'
                       '{PROJECTNAME}_{SHOTNAME}_{TASKNAME}.{FRAMENUMBER}.{EXT}')


class DeliSys(QtWidgets.QWidget):
    def __init__(self):
        super(DeliSys, self).__init__()
        self.setWindowTitle('Deli Sys')
        self.setMinimumWidth(1000)
        self.setMinimumHeight(400)
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        """
        Create all the widgets required for the tool here
        :return: None
        """
        self.src_dir_ledit = QtWidgets.QLineEdit()
        self.src_dir_ledit.setPlaceholderText('Source Directory')
        self.src_dir_ledit.installEventFilter(QLineEditDropHandler(self.src_dir_ledit))
        self.output_dir_ledit = QtWidgets.QLineEdit()
        self.output_dir_ledit.setPlaceholderText('Output Directory')
        self.output_dir_ledit.installEventFilter(QLineEditDropHandler(self.output_dir_ledit))
        self.browse_btn1 = QtWidgets.QPushButton('Browse')
        self.browse_btn2 = QtWidgets.QPushButton('Browse')
        self.add_btn = QtWidgets.QPushButton('Load')
        self.add_btn.setFixedWidth(80)
        self.deliver_btn = QtWidgets.QPushButton('Deliver')

        self.table = QtWidgets.QTreeWidget()
        self.table.setHeaderLabels(['Source Files', 'Destination Files'])
        self.table.setColumnWidth(0, 550)
        self.table.setColumnWidth(1, 550)

    def create_layout(self):
        """
        Create layouts for the tool and put all the widgets in those layouts
        Returns: None
        """
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)  # sets the main_layout
        self.main_layout.setAlignment(QtCore.Qt.AlignTop)

        self.vbox1 = QtWidgets.QVBoxLayout()
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.src_dir_ledit)
        hbox1.addWidget(self.browse_btn1)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.output_dir_ledit)
        hbox2.addWidget(self.browse_btn2)
        self.vbox1.addLayout(hbox1)
        self.vbox1.addLayout(hbox2)
        self.main_layout.addLayout(self.vbox1)

        bottom_hbox = QtWidgets.QHBoxLayout()
        bottom_hbox.addWidget(self.add_btn)
        bottom_hbox.addWidget(self.deliver_btn)
        self.main_layout.addLayout(bottom_hbox)
        self.main_layout.addWidget(self.table)

    def create_connections(self):
        """
        Function to connect the buttons to the functionality
        Returns: None
        """
        self.browse_btn1.clicked.connect(self.browse_src_files)
        self.browse_btn2.clicked.connect(self.browse_dest_files)
        self.add_btn.clicked.connect(lambda: self.load_data(self.src_dir_ledit.text()))
        self.deliver_btn.clicked.connect(self.deliver_data)

    def browse_src_files(self):
        """
        Function to browse a source directory & load data to the table
        Returns: None
        """
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dirname = file_dialog.getExistingDirectory()
        self.src_dir_ledit.setText(dirname)
        files_path = self.src_dir_ledit.text()
        self.load_data(files_path)

    def browse_dest_files(self):
        """
        Function to select a output directory
        Returns: None
        """
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dirname = file_dialog.getExistingDirectory()
        self.src_dir_ledit.setText(dirname)
        files_path = self.src_dir_ledit.text()
        self.load_data(files_path)

    def load_data(self, files_path):
        if not files_path:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText("Input directory field cannot be empty!")
            msgBox.setWindowTitle("Warning")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec()
            return
        table_dict = {}
        for file in os.listdir(files_path):
            name, ext = os.path.splitext(file)
            ext = ext[1:]
            _filepath = os.path.join(files_path, file)
            if ext not in table_dict:
                table_dict.setdefault(ext, [_filepath])
            else:
                table_dict[ext].append(_filepath)

        output_dir = self.output_dir_ledit.text()
        for ext, images in table_dict.items():
            ext_item = QtWidgets.QTreeWidgetItem([ext.upper()])
            self.table.addTopLevelItem(ext_item)
            for image in images:
                project_name = os.path.basename(image).split('_')[0]
                shot_name = os.path.basename(image).split('_')[1]
                task_name = os.path.basename(image).split('_')[-1].split('.')[0]
                frame_number = os.path.basename(image).split('_')[-1].split('.')[1]
                current_date = datetime.today().strftime('%Y%m%d%H%M')
                data = {
                    'OUTPUT_DIR': output_dir,
                    'DATE': current_date,
                    'PROJECTNAME': project_name,
                    'SHOTNAME': shot_name,
                    'TASKNAME': task_name,
                    'FRAMENUMBER': frame_number,
                    'EXT': ext
                }
                dest_file_path = template.format(data)
                ext_item.addChild(QtWidgets.QTreeWidgetItem([image, dest_file_path]))

    def deliver_data(self):
        output_dir = self.output_dir_ledit.text()
        if not output_dir:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText("Output directory field cannot be empty!")
            msgBox.setWindowTitle("Warning")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec()
        for i in range(self.table.topLevelItemCount()):
            file_type_item = self.table.topLevelItem(i)
            for child_num in range(file_type_item.childCount()):
                child = file_type_item.child(child_num)
                if os.path.exists(os.path.dirname(child.text(1))):
                    # run your copy tool or function here
                    shutil.copy2(child.text(0), child.text(1))
                else:
                    os.makedirs(os.path.dirname(child.text(1)))
                    # run your copy tool or function here
                    shutil.copy2(child.text(0), child.text(1))


class QLineEditDropHandler(QtCore.QObject):
    """
    Class to handle drag & drop events on the QlineEdit widget
    """

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.DragEnter:
            data = event.mimeData()
            urls = data.urls()
            if urls and urls[0].scheme() == 'file':
                event.acceptProposedAction()

        if event.type() == QtCore.QEvent.DragMove:
            data = event.mimeData()
            urls = data.urls()
            if urls and urls[0].scheme() == 'file':
                event.acceptProposedAction()

        if event.type() == QtCore.QEvent.Drop:
            data = event.mimeData()
            urls = data.urls()
            if urls and urls[0].scheme() == 'file':
                filepath = str(urls[0].path())[1:]
                watched.setText(filepath)
                return True
        return super().eventFilter(watched, event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = DeliSys()
    dialog.show()
    sys.exit(app.exec_())
