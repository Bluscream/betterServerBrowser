from ts3plugin import ts3plugin, PluginHost
from pytsonui import setupUi
from PythonQt.QtGui import QDialog, QListWidgetItem, QWidget, QComboBox, QPalette, QTableWidgetItem, QMenu, QAction, QCursor
from PythonQt.QtCore import Qt
import ts3, ts3defines, datetime, os, requests, json, configparser, webbrowser, traceback


class serverBrowser(ts3plugin):
    name = "Better Server Browser"
    apiVersion = 21
    requestAutoload = True
    version = "1.0"
    author = "Bluscream"
    description = "A better serverlist provided by PlanetTeamspeak.\n\nCheck out https://r4p3.net/forums/plugins.68/ for more plugins."
    offersConfigure = False
    commandKeyword = ""
    infoTitle = ""
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Browse Servers", "scripts/serverBrowser/gfx/icon.png"),(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 1, "View on PT", "")]
    hotkeys = []
    debug = False
    ini = os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "serverBrowser", "cfg", "serverBrowser.ini")
    config = configparser.ConfigParser()

    def __init__(self):
        if os.path.isfile(self.ini):
            self.config.read(self.ini)
            #for key, value in self.config["FILTERS"].items():
                #ts3.printMessageToCurrentTab(str(key).title()+": "+str(value))
        else:
            self.config['GENERAL'] = { "Debug": "False", "API": "" }
            self.config['FILTERS'] = {
                "serverNameModifier": "Contains", "filterServerName": "", "countryBox": "",
                "hideEmpty": "False", "hideFull": "False", "maxUsers": "False", "maxUsersMin": "0", "maxUsersMax": "0",
                "maxSlots": "False", "maxSlotsMin": "0", "maxSlotsMax": "0", "filterPassword": "all", "filterChannels": "all"
            }
            with open(self.ini, 'w') as configfile:
                self.config.write(configfile)

        ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/Bluscream]Bluscream[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0:
                self.dlg = ServersDialog(self)
                self.dlg.show()
                #ts3.printMessageToCurrentTab(str(self.filters))
            elif menuItemID == 1:
                _schid = ts3.getCurrentServerConnectionHandlerID()
                (error, _clid) = ts3.getClientID(_schid)
                (error, _ip) = ts3.getConnectionVariableAsString(_schid,_clid,ts3defines.ConnectionProperties.CONNECTION_SERVER_IP)
                (error, _port) = ts3.getConnectionVariableAsString(_schid,_clid,ts3defines.ConnectionProperties.CONNECTION_SERVER_PORT)
                url = ""
                if _port != "":
                    _url = "https://www.planetteamspeak.com/serverlist/result/server/ip/"+_ip+":"+_port+"/"
                else:
                    _url = "https://www.planetteamspeak.com/serverlist/result/server/ip/"+_ip+"/"
                ts3.printMessageToCurrentTab(str("Navigating to \""+_url+"\""))
                webbrowser.open(_url)

class ServersDialog(QDialog):
    page = 1
    pages = 0
    countries = []
    API_PREFIX = "https://"
    API_DOMAIN = "api.planetteamspeak.com"
    API_BASE = API_PREFIX+API_DOMAIN+"/"
    NAME_MODIFIERS = ["Contains", "Starts with", "Ends with"]
    CONF_WIDGETS = [
                        ("serverList", True, []),
                        ("serverNameModifier", True, []),
                        ("filterServerName", True, []),
                        ("locationGroup", False, [
                            ("countryBox", True, [])
                        ]),
                        ("usersGroup", False, [
                            ("hideEmpty", True, []),
                            ("hideFull", True, []),
                            ("maxUsers", True, []),
                            ("maxUsersMin", True, []),
                            ("maxUsersMax", True, [])
                        ]),
                        ("slotsGroup", False, [
                            ("maxSlots", True, []),
                            ("maxSlotsMin", True, []),
                            ("maxSlotsMax", True, [])
                        ]),
                        ("passwordGroup", False, [
                            ("filterPasswordShowAll", True, []),
                            ("filterPasswordShowWith", True, []),
                            ("filterPasswordShowWithout", True, [])
                        ]),
                        ("channelsGroup", False, [
                            ("filterChannelsCanCreate", True, []),
                            ("filterChannelsCantCreate", True, []),
                            ("filterChannelsShowAll", True, [])
                        ]),
                        ("status", True, []),
                        ("info", True, []),
                        ("pageLabel", True, []),
                        ("apply", True, []),
                        ("reload", True, []),
                        ("previous", True, []),
                        ("next", True, [])
                    ]
    def buhl(self, s):
        if s.lower() == 'true' or s == 1:
            return True
        elif s.lower() == 'false' or s == 0:
            return False
        else:
            raise ValueError("Cannot convert {} to a bool".format(s))

    def __init__(self,serverBrowser, parent=None):
        self.serverBrowser=serverBrowser
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "serverBrowser", "ui", "servers.ui"), self.CONF_WIDGETS)
        self.setupList()
        self.setWindowTitle("PlanetTeamspeak Server Browser")
        #self.apply.connect("clicked()", self.on_apply_clicked)
        #self.reload.connect("clicked()", self.on_reload_clicked)
        #self.ReasonList.connect("currentItemChanged(QListWidgetItem*, QListWidgetItem*)", self.onReasonListCurrentItemChanged)
        #self.ReasonList.connect("itemChanged(QListWidgetItem*)", self.onReasonListItemChanged)

    def setupList(self):
        self.serverNameModifier.addItems(self.NAME_MODIFIERS)
        #self.cfg.set("general", "differentApi", "True" if state == Qt.Checked else "False")
        self.requestAvailableCountries()
        self.countryBox.addItems([x[1] for x in self.countries])
        #ReportDialog.ReasonList.clear()
        self.setupFilters()
        # self.serverList.doubleClicked.connect(self.doubleClicked_table)
        #ts3.printMessageToCurrentTab(str(serverBrowser.filters))
        #if serverBrowser.filters.filterServerName != "":
            #self.filterServerName.setText(serverBrowser.filters.filterServerName)
        #item.setFlags(item.flags() &~ Qt.ItemIsEditable)
        # self.countryBox.clear()
        #for item in countries:
            #self.countryBox.addItem(str(item[1]))
        #self.serverList.setStretchLastSection(true)
        self.listServers(self.page)

    def setupFilters(self):
        try:
            _filters = self.serverBrowser.config["FILTERS"]
            buhl = self.buhl
            self.hideEmpty.setChecked(buhl(_filters["hideEmpty"]))
            self.hideFull.setChecked(buhl(_filters["hideFull"]))
            self.maxUsers.setChecked(buhl(_filters["maxUsers"]))
            self.maxUsersMin.setValue(int(_filters["maxUsersMin"]))
            self.maxUsersMax.setValue(int(_filters["maxUsersMax"]))
            self.maxSlots.setChecked(buhl(_filters["maxSlots"]))
            self.maxSlotsMin.setValue(int(_filters["maxSlotsMin"]))
            self.maxSlotsMax.setValue(int(_filters["maxSlotsMax"]))
            if _filters["filterPassword"] == "none":
                self.filterPasswordShowWithout.setChecked(True)
                #self.filterPasswordShowWith.setChecked(False)
                #self.filterPasswordShowAll.setChecked(False)
            elif _filters["filterPassword"] == "only":
                #self.filterPasswordShowWithout.setChecked(False)
                self.filterPasswordShowWith.setChecked(True)
                #self.filterPasswordShowAll.setChecked(False)
            else:
                #self.filterPasswordShowWithout.setChecked(False)
                #self.filterPasswordShowWith.setChecked(False)
                self.filterPasswordShowAll.setChecked(True)
            if _filters["filterChannels"] == "none":
                self.filterChannelsCantCreate.setChecked(True)
                #self.filterChannelsCanCreate.setChecked(False)
                #self.filterChannelsShowAll.setChecked(False)
            elif _filters["filterChannels"] == "only":
                #self.filterChannelsCantCreate.setChecked(False)
                self.filterChannelsCanCreate.setChecked(True)
                #self.filterChannelsShowAll.setChecked(False)
            else:
                #self.filterChannelsCantCreate.setChecked(False)
                #self.filterChannelsCanCreate.setChecked(False)
                self.filterChannelsShowAll.setChecked(True)
            self.serverNameModifier.setCurrentText(_filters["serverNameModifier"])
            self.countryBox.setCurrentText(_filters["countryBox"])
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    # def doubleClicked_table(self):
    #     index = self.serverList.selectedIndexes()[0]
    #     id_us = int(self.serverList.model().data(index).toString())
    #     ts3.printMessageToCurrentTab("index : " + str(id_us))

    def contextMenuEvent(self, event):
        self.serverList = QMenu(self)
        connectAction = QAction("scripts/serverBrowser/gfx/icon.png", 'Connect', self)
        connectAction.triggered.connect(self.connect)
        self.serverList.addAction(connectAction)
        self.serverList.popup(QCursor.pos())

    def connect(self):
        index = self.serverList.selectedIndexes()[0]
        id_us = int(self.serverList.model().data(index).toString())
        ts3.printMessageToCurrentTab("index : " + str(id_us))

    def requestAvailableCountries(self):
        countries = requests.get(self.API_BASE+"servercountries")
        self.status.setText("Response from \""+self.API_DOMAIN+"\": "+str(countries.status_code)+": "+countries.reason)
        palette = QPalette()
        if countries.status_code == 200:
            palette.setColor(QPalette.Foreground,Qt.darkGreen)
            self.countryBox.clear()
        else:
            palette.setColor(QPalette.Foreground,Qt.red)
        self.status.setPalette(palette)
        countries = countries.content.decode('utf-8')
        countries = json.loads(countries)["result"]["data"]
        countries = [['ALL', 'All', 0]]+countries
        self.countries = countries[0:2]+sorted(countries[2:],key=lambda x: x[1])
        #__countries = __countries.__add__([['ALL', 'All', 0]])
        # ts3.printMessageToCurrentTab(str(countries))

    def requestServers(self, filters = []):

        servers = requests.get(self.API_BASE+"serverlist/?page="+str(self.page)+"&limit=30")
        self.status.setText("Response from \""+self.API_DOMAIN+"\": "+str(servers.status_code)+": "+servers.reason)
        palette = QPalette()
        if not servers.status_code == 200:
            palette.setColor(QPalette.Foreground,Qt.red)
        self.status.setPalette(palette)
        _servers = servers.content.decode('utf-8')
        __servers = json.loads(_servers)
        return __servers
    i = 0
    def listServers(self, filters = []):
        self.i = self.i+1
        ts3.printMessageToCurrentTab(str(self.i))
        servers = self.requestServers()
        palette = QPalette()
        self.status.setText("Status: "+servers["status"].title())
        if servers["status"] == "success":
            self.pageLabel.setText(str(servers["result"]["pageactive"])+" / "+str(servers["result"]["pagestotal"]))
            self.info.setText(str(servers["result"]["itemsshown"])+" / "+str(servers["result"]["itemstotal"])+" Servers shown.")
            self.serverList.setRowCount(0)
        else:
            self.info.setText("Requested Page: "+self.page)
            palette.setColor(QPalette.Foreground,Qt.red)
        self.status.setPalette(palette)
        _list = self.serverList
        for key in servers["result"]["data"]:
            #ts3.printMessageToCurrentTab(str(key))
            rowPosition = _list.rowCount
            _list.insertRow(rowPosition)
            #_list.setFlags()
            if key['premium']:
                _list.setItem(rowPosition, 0, QTableWidgetItem("Yes"))
            else:
                _list.setItem(rowPosition, 0, QTableWidgetItem("No"))
            _list.setItem(rowPosition, 1, QTableWidgetItem(key['name']))
            _list.setItem(rowPosition, 2, QTableWidgetItem(str(key['users'])+' / '+str(key['slots'])))
            if key['users'] >= key['slots']:
                palette.setColor(QPalette.Foreground,Qt.red)
                _list.setPalette(palette)
            _list.setItem(rowPosition, 3, QTableWidgetItem(str(key['country'])))
            if key['password']:
                _list.setItem(rowPosition, 4, QTableWidgetItem("Yes"))
            else:
                _list.setItem(rowPosition, 4, QTableWidgetItem("No"))
            if key['premium']:
                _list.setItem(rowPosition, 5, QTableWidgetItem("Yes"))
            else:
                _list.setItem(rowPosition, 5, QTableWidgetItem("No"))

    #def onReasonListItemChanged(self, item):
        #checked = item.checkState() == Qt.Checked
        #name = item.data(Qt.UserRole)

        #if checked and name not in self.host.active:
            #self.host.activate(name)
        #elif not checked and name in self.host.active:
            #self.host.deactivate(name)

        #if self.pluginsList.currentItem() == item:
            #self.settingsButton.setEnabled(checked and name in self.host.active and self.host.active[name].offersConfigure)

    def on_apply_clicked(self):
        try:
            self.serverBrowser.config.set("FILTERS", "hideEmpty", str(self.hideEmpty.isChecked()))
            self.serverBrowser.config.set("FILTERS", "hideFull", str(self.hideFull.isChecked()))
            self.serverBrowser.config.set("FILTERS", "maxUsers", str(self.maxUsers.isChecked()))
            self.serverBrowser.config.set("FILTERS", "maxUsersMin", str(self.maxUsersMin.value))
            self.serverBrowser.config.set("FILTERS", "maxUsersMax", str(self.maxUsersMax.value))
            self.serverBrowser.config.set("FILTERS", "maxSlots", str(self.maxSlots.isChecked()))
            self.serverBrowser.config.set("FILTERS", "maxSlotsMin", str(self.maxSlotsMin.value))
            self.serverBrowser.config.set("FILTERS", "maxSlotsMax", str(self.maxSlotsMax.value))
            if self.filterPasswordShowWithout.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterPassword", "none")
            elif self.filterPasswordShowWith.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterPassword", "only")
            elif self.filterPasswordShowAll.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterPassword", "all")
            if self.filterChannelsCantCreate.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterChannels", "none")
            elif self.filterChannelsCanCreate.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterChannels", "only")
            elif self.filterChannelsShowAll.isChecked():
                self.serverBrowser.config.set("FILTERS", "filterChannels", "all")
            self.serverBrowser.config.set("FILTERS", "serverNameModifier", self.serverNameModifier.currentText)
            self.serverBrowser.config.set("FILTERS", "countryBox", self.countryBox.currentText)
            with open(self.serverBrowser.ini, 'w') as configfile:
                self.serverBrowser.config.write(configfile)
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "pyTSon", 0)

    def on_reload_clicked(self):
        try:
            self.listServers(self.page)
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)

    def on_previous_clicked(self):
        try:
            if self.page > 1:
                self.page -= 1
                self.listServers(self.page)
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
    def on_next_clicked(self):
        try:
            self.page += 1
            self.listServers(self.page)
        except:
            ts3.logMessage(traceback.format_exc(), ts3defines.LogLevel.LogLevel_ERROR, "PyTSon", 0)
