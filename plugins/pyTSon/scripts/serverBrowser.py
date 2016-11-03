from ts3plugin import ts3plugin, PluginHost
from pytsonui import setupUi
from PythonQt.QtGui import QDialog, QListWidgetItem, QWidget, QComboBox
import ts3, ts3defines, datetime, os, requests, json

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
    menuItems = [(ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL, 0, "Browse Servers", "scripts/serverBrowser/gfx/icon.png")]
    hotkeys = []
    debug = False


    def __init__(self):
        ts3.printMessageToCurrentTab('[{:%Y-%m-%d %H:%M:%S}]'.format(datetime.datetime.now())+" [color=orange]"+self.name+"[/color] Plugin for pyTSon by [url=https://github.com/Bluscream]Bluscream[/url] loaded.")

    def onMenuItemEvent(self, schid, atype, menuItemID, selectedItemID):
        if atype == ts3defines.PluginMenuType.PLUGIN_MENU_TYPE_GLOBAL:
            if menuItemID == 0:
                self.dlg = ServersDialog(None)
                self.dlg.show()

class ServersDialog(QDialog):
    #[(objectName, store, [children])]
    API_PREFIX = "https://"
    API_DOMAIN = "api.planetteamspeak.com"
    API_BASE = API_PREFIX+API_DOMAIN+"/"
    NAME_MODIFIERS = ["Contains", "Starts with", "Ends with"]
    CONF_WIDGETS = [
                        ("serverList", True, []),
                        ("serverNameModifier", True, []),
                        ("filterServerName", True, []),
                        ("locationGroup", False, [
                            ("countryBox", True, []),
                            ("regionBox", True, []),
                            ("cityBox", True, [])
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
                        ("apply", True, []),
                        ("reload", True, []),
                        ("status", True, [])
                    ]

    def __init__(self, parent):
        super(QDialog, self).__init__(parent)
        setupUi(self, os.path.join(ts3.getPluginPath(), "pyTSon", "scripts", "serverBrowser", "ui", "servers.ui"), self.CONF_WIDGETS)
        self.setupList()

        #self.ReasonList.connect("currentItemChanged(QListWidgetItem*, QListWidgetItem*)", self.onReasonListCurrentItemChanged)
        #self.ReasonList.connect("itemChanged(QListWidgetItem*)", self.onReasonListItemChanged)


    def setupList(self):
        #ReportDialog.ReasonList.clear()
        self.serverNameModifier.addItems(self.NAME_MODIFIERS)
        #item.setFlags(item.flags() &~ Qt.ItemIsEditable)
        servers = requests.get(self.API_BASE+"serverlist/?limit=1")
        self.status.setText("Response from: "+str(servers.status_code)+": "+servers.reason)
        ts3.printMessageToCurrentTab(str(servers.content))

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
            schid = ts3.getCurrentServerConnectionHandlerID()
            ts3.requestSendPrivateTextMsg(schid, "Reported", 0)

        def on_reload_clicked(self):
            self.hide()
