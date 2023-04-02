from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from krita import *
import struct
import zlib
import json
from urllib.request import Request, urlopen
from io import BytesIO

from .utils import decode_base64_to_image, decompress_png
from krita import *

import random

class MyDocker(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Disco Spinach")
        mainWidget = QWidget(self)
        self.setWidget(mainWidget)

        prompt_label = QLabel("Prompt:")
        prompt_label.setAlignment(Qt.AlignBottom)

        default_prompt = "Magical Forest Island, by Studio Ghibli and Carl Spitzweg"
        self.input_text = QPlainTextEdit(default_prompt, mainWidget)
        self.input_text.textChanged.connect(self.prompt_changed)
        self.text_in = default_prompt

        #width_label = QLabel("Width:")
        # width widget
        width_widget = QSpinBox()
        width_widget.setMinimum(512)
        width_widget.setMaximum(1280)
        width_widget.setSingleStep(64)
        width_widget.valueChanged.connect(self.width_value_changed)
        self.width_val = 512

        #height_label = QLabel("Height:")
        # height widget
        height_widget = QSpinBox()
        height_widget.setMinimum(512)
        height_widget.setMaximum(1280)
        height_widget.setSingleStep(64)
        height_widget.valueChanged.connect(self.height_value_changed)
        self.height_val = 512

        w_label = QLabel("Width:")
        w_label.setAlignment(Qt.AlignBottom)
        h_label = QLabel("Height:")
        h_label.setAlignment(Qt.AlignBottom)

        w_h_labels = QHBoxLayout()
        #width_labeled.addWidget(width_label)
        #width_labeled.addWidget(width_widget)
        #w_h_labels = QHBoxLayout()
        w_h_labels.addWidget(w_label)
        w_h_labels.addWidget(h_label)

        #height_labeled = QVBoxLayout()
        #height_labeled.addWidget(height_label)
        #height_labeled.addWidget(height_widget)
        w_h_layout = QHBoxLayout()
        w_h_layout.addWidget(width_widget)
        w_h_layout.addWidget(height_widget)
        #w_h_layout = QHBoxLayout()
        #w_h_layout.addLayout(width_labeled)
        #w_h_layout.addLayout(height_labeled)

        steps_label = QLabel("Steps:")
        steps_label.setAlignment(Qt.AlignBottom)

        steps_widget = QSpinBox()
        steps_widget.setMinimum(10)
        steps_widget.setMaximum(1000)
        steps_widget.setSingleStep(10)
        steps_widget.setValue(100)
        steps_widget.valueChanged.connect(self.steps_value_changed)
        self.steps_val = 100

        init_str_label = QLabel("Skip Steps (%):")
        init_str_label.setAlignment(Qt.AlignBottom)

        init_str_widget = QSpinBox()
        init_str_widget.setMinimum(0)
        init_str_widget.setMaximum(100)
        init_str_widget.setSingleStep(1)
        init_str_widget.setValue(50)
        init_str_widget.valueChanged.connect(self.skip_steps_changed)
        self.skip_steps = 50

        init_scale_label = QLabel("Init Scale:")
        init_scale_label.setAlignment(Qt.AlignBottom)
        
        # init_scale_widget = QSpinBox()
        # init_scale_widget.setMinimum(0)
        # init_scale_widget.setMaximum(100000)
        # init_scale_widget.setSingleStep(100)
        # init_scale_widget.setValue(1000)
        # init_scale_widget.valueChanged.connect(self.init_scale_value_changed)
        # self.init_scale_val = 1000
        default_init_scale = '1000|1200'
        init_scale_widget = QLineEdit(default_init_scale)
        init_scale_widget.textChanged.connect(self.init_scale_value_changed)
        self.init_scale_val = default_init_scale

        step_param_labels = QHBoxLayout()
        step_param_labels.addWidget(steps_label)
        step_param_labels.addWidget(init_str_label)

        step_param_layout = QHBoxLayout()
        step_param_layout.addWidget(steps_widget)
        step_param_layout.addWidget(init_str_widget)
        #step_param_layout.addWidget(init_scale_widget)

        cgs_label = QLabel("Clip Guidance Scale:")
        cgs_label.setAlignment(Qt.AlignBottom)

        #cgs_widget = QSpinBox()
        #cgs_widget.setMinimum(1000)
        #cgs_widget.setMaximum(100000)
        #cgs_widget.setSingleStep(100)
        #cgs_widget.setValue(6000)
        #cgs_widget.valueChanged.connect(self.cgs_value_changed)
        #self.cgs_val = 6000
        default_cgs = '6000|5000|4000'
        cgs_widget = QLineEdit(default_cgs)
        cgs_widget.textChanged.connect(self.cgs_value_changed)
        self.cgs_val = default_cgs

        range_scale_label = QLabel("Range Scale:")
        range_scale_label.setAlignment(Qt.AlignBottom)

        # default_range_scale_val = 150
        # range_scale_widget = QSpinBox()
        # range_scale_widget.setMinimum(0)
        # range_scale_widget.setMaximum(1000)
        # range_scale_widget.setSingleStep(5)
        # range_scale_widget.setValue(default_range_scale_val)
        # range_scale_widget.valueChanged.connect(self.range_scale_value_changed)
        # self.range_scale_val = default_range_scale_val
        default_range_scale_val = '150|120'
        range_scale_widget = QLineEdit(default_range_scale_val)
        range_scale_widget.textChanged.connect(self.range_scale_value_changed)
        self.range_scale_val = default_range_scale_val

        clamp_max_label = QLabel("Clamp Max Gradient (10th of %):")
        clamp_max_label.setAlignment(Qt.AlignBottom)

        # default_clamp_max_val = 50
        # clamp_max_widget = QSpinBox()
        # clamp_max_widget.setMinimum(5)
        # clamp_max_widget.setMaximum(1000)
        # clamp_max_widget.setSingleStep(5)
        # clamp_max_widget.setValue(default_clamp_max_val)
        # clamp_max_widget.valueChanged.connect(self.clamp_max_value_changed)
        # self.clamp_max_val = default_clamp_max_val
        default_clamp_max_val = '50|60'
        clamp_max_widget = QLineEdit(default_clamp_max_val)
        clamp_max_widget.textChanged.connect(self.clamp_max_value_changed)
        self.clamp_max_val = default_clamp_max_val

        cut_pow_label = QLabel("Cut Power (%):")
        cut_pow_label.setAlignment(Qt.AlignBottom)

        default_cut_pow_val = 50
        cut_pow_widget = QSpinBox()
        cut_pow_widget.setMinimum(5)
        cut_pow_widget.setMaximum(100)
        cut_pow_widget.setSingleStep(5)
        cut_pow_widget.setValue(default_cut_pow_val)
        cut_pow_widget.valueChanged.connect(self.cut_pow_value_changed)
        self.cut_pow_val = default_cut_pow_val

        scale_param_labels = QHBoxLayout()
        scale_param_labels.addWidget(init_scale_label)
        scale_param_labels.addWidget(cgs_label)
        scale_param_labels.addWidget(range_scale_label)
        #scale_params_labels.addWidget(clamp_max_label)
        #scale_params_labels.addWidget(cut_pow_label)
        scale_param_labels.setAlignment(Qt.AlignBottom)

        scale_param_layout = QHBoxLayout()
        scale_param_layout.addWidget(init_scale_widget)
        scale_param_layout.addWidget(cgs_widget)
        scale_param_layout.addWidget(range_scale_widget)
        #scale_params_layout.addWidget(clamp_max_widget)
        #scale_params_layout.addWidget(cut_pow_widget)

        #advanced_param_labels = QHBoxLayout()
        #advanced_param_labels.addWidget(clamp_max_label)
        #advanced_param_labels.addWidget(cut_pow_label)

        #advanced_param_layout = QHBoxLayout()
        #advanced_param_layout.addWidget(clamp_max_widget)
        #advanced_param_layout.addWidget(cut_pow_widget)

        seed_label = QLabel("Seed:")
        seed_label.setAlignment(Qt.AlignBottom)

        self.seed_widget = QSpinBox()
        self.seed_widget.setMinimum(0)
        self.seed_widget.setMaximum(100000)
        self.seed_widget.setSingleStep(1)
        self.seed_widget.setValue(42)
        self.seed_widget.valueChanged.connect(self.seed_value_changed)
        self.seed_val = 42

        self.random_seed_widget = QCheckBox("Randomize Seed After Bake", self)
        self.random_seed_widget.setChecked(True)

        seed_param_layout = QHBoxLayout()
        seed_param_layout.addWidget(self.seed_widget)
        seed_param_layout.addWidget(self.random_seed_widget)

        local_url_label = QLabel("Local URL:")
        local_url_label.setAlignment(Qt.AlignBottom)

        default_local_url = "http://127.0.0.1:7860"
        local_url_widget = QLineEdit(default_local_url)
        local_url_widget.textChanged.connect(self.local_url_changed)
        self.local_url = default_local_url

        selectionButton = QPushButton("Fix Selection Size", mainWidget)
        selectionButton.clicked.connect(self.fix_selection_size)

        generateButton = QPushButton("Generate", mainWidget)
        generateButton.clicked.connect(self.generate_image)

        mainWidget.setLayout(QVBoxLayout())
        mainWidget.layout().addWidget(prompt_label)
        mainWidget.layout().addWidget(self.input_text)
        mainWidget.layout().addLayout(w_h_labels)
        mainWidget.layout().addLayout(w_h_layout)
        #mainWidget.layout().addWidget(steps_label)
        #mainWidget.layout().addWidget(steps_widget)
        #mainWidget.layout().addLayout(main_param_labels)
        #mainWidget.layout().addLayout(main_param_layout)
        mainWidget.layout().addLayout(step_param_labels)
        mainWidget.layout().addLayout(step_param_layout)
        #mainWidget.layout().addLayout(advanced_params_labels)
        #mainWidget.layout().addLayout(advanced_params_layout)
        mainWidget.layout().addLayout(scale_param_labels)
        mainWidget.layout().addLayout(scale_param_layout)
        #mainWidget.layout().addLayout(advanced_param_labels)
        #mainWidget.layout().addLayout(advanced_param_layout)
        #mainWidget.layout().addWidget(cgs_label)
        #mainWidget.layout().addWidget(cgs_widget)
        #mainWidget.layout().addWidget(range_scale_label)
        #mainWidget.layout().addWidget(range_scale_widget)
        mainWidget.layout().addWidget(clamp_max_label)
        mainWidget.layout().addWidget(clamp_max_widget)
        mainWidget.layout().addWidget(cut_pow_label)
        mainWidget.layout().addWidget(cut_pow_widget)
        mainWidget.layout().addWidget(seed_label)
        mainWidget.layout().addLayout(seed_param_layout)
        #mainWidget.layout().addWidget(self.seed_widget)
        #mainWidget.layout().addWidget(self.randomize_seed_widget)
        #mainWidget.layout().addLayout(init_param_labels)
        #mainWidget.layout().addLayout(init_param_layout)
        #mainWidget.layout().addWidget(init_str_label)
        #mainWidget.layout().addWidget(init_str_widget)
        #mainWidget.layout().addWidget(init_scale_label)
        #mainWidget.layout().addWidget(init_scale_widget)
        mainWidget.layout().addWidget(local_url_label)
        mainWidget.layout().addWidget(local_url_widget)
        mainWidget.layout().addWidget(selectionButton)
        mainWidget.layout().addWidget(generateButton)

    def prompt_changed(self):
        self.text_in = self.input_text.toPlainText()
        pass
        #self.text_in = s

    def width_value_changed(self, i):
        self.width_val = i

    def height_value_changed(self, i):
        self.height_val = i

    def steps_value_changed(self, i):
        self.steps_val = i

    #def cgs_value_changed(self, i):
    #    self.cgs_val = i
    def cgs_value_changed(self, s):
        self.cgs_val = s

    #def range_scale_value_changed(self, i):
    #    self.range_scale_val = i
    def range_scale_value_changed(self, s):
        self.range_scale_val = s

    #def clamp_max_value_changed(self, i):
    #    self.clamp_max_val = i
    def clamp_max_value_changed(self, s):
        self.clamp_max_val = s

    def cut_pow_value_changed(self, i):
        self.cut_pow_val = i

    def seed_value_changed(self, i):
        self.seed_val = i

    def skip_steps_changed(self, i):
        self.skip_steps = i

    # def init_scale_value_changed(self, i):
    #     self.init_scale_val = i
    def init_scale_value_changed(self, s):
        self.init_scale_val = s

    def local_url_changed(self, s):
        self.local_url = s

    def fix_selection_size(self):
        app = Krita.instance()
        doc = app.activeDocument()
        selection = doc.selection()

        if selection is not None:
            pos_x = selection.x()
            pos_y = selection.y()
            init_w = selection.width()
            init_h = selection.height()
            s = Selection()
            w, h = self.width_val, self.height_val
            out_res = w / h
            init_w = out_res * init_h
            s.select(pos_x, pos_y, init_w, init_h, 255)
            doc.setSelection(s)
            
    
    def generate_image(self):
        app = Krita.instance()
        doc = app.activeDocument()
        root = doc.rootNode()
        oldLayer = doc.activeNode()
        #app.action('duplicatelayer').trigger()
        #app.action('move_layer_up').trigger()
        layer = doc.createNode(self.text_in[:14] + "...(Disco Dream) " + str(self.seed_val), "paintlayer")
        root.addChildNode(layer, None)
        doc.setActiveNode(layer)

        doc.refreshProjection()
        #layer = doc.nodeByName("Copy of " + oldLayer.name())

        assert layer != None

        #init_w = doc.width()
        #init_h = doc.height()
        selection = doc.selection()

        if selection is None:
            pos_x = 0
            pos_y = 0
            init_w = doc.width()
            init_h = doc.height()
        else:
            pos_x = selection.x()
            pos_y = selection.y()
            init_w = selection.width()
            init_h = selection.height()

        init_dims = str(init_w) + ", " + str(init_h)

        w, h = self.width_val, self.height_val
        dims = str(w) + ", " + str(h)

        # Set the API endpoint
        url_api = "/api/predict/"

        oldLayerBytesStr = str(oldLayer.pixelData(pos_x, pos_y, init_w, init_h))
        # Set the data to be sent in the request
        data = {"data": [self.text_in, dims, self.steps_val, self.cgs_val, 
                         self.range_scale_val, self.clamp_max_val, self.cut_pow_val,
                         self.seed_val, oldLayerBytesStr, 
                         self.skip_steps / 100, self.init_scale_val, init_dims]}

        # Convert the data to JSON
        json_data = json.dumps(data).encode()
        # Set the headers for the request
        headers = {'Content-Type': 'application/json'}
        # Create the request object
        req = Request(self.local_url + url_api, json_data, headers)
        # Send the request
        response = urlopen(req)
        # Get the response data
        response_data = json.loads(response.read())

        imgData = response_data['data']
        out = decode_base64_to_image(imgData[0])

        f = BytesIO(out)
        out = decompress_png(f)
        print(len(out))
        layer.setPixelData(out, pos_x, pos_y, init_w, init_h)
        if self.random_seed_widget.isChecked():
            randomSeed = random.randint(0, 100000)
            self.seed_widget.setValue(randomSeed)
            self.seed_val = randomSeed
        doc.refreshProjection()

    def canvasChanged(self, canvas):
        pass

Krita.instance().addDockWidgetFactory(DockWidgetFactory("Disco Spinach", DockWidgetFactoryBase.DockRight, MyDocker))
