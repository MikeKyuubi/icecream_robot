import QtQuick
import QtQuick.Window
import QtQuick.Layouts

Window {
    id: window
    visible: true
    width: 780
    height: 620
    minimumWidth: 700
    minimumHeight: 580
    title: "Ice Cream Selector"
    color: "#F7F4EF"

    property string activeFlavor: ""
    property string currentPage: "selector"
    property bool orderComplete: false

    readonly property var flavorOrder: ["vanilla", "chocolate", "mixed"]

    // ── 3 second delay before returning to selector ───────────────────────────
    Timer {
        id: returnTimer
        interval: 3000
        repeat: false
        onTriggered: {
            window.currentPage = "selector"
            window.activeFlavor = ""
            window.orderComplete = false
        }
    }

    // ── Watch robot state and trigger return ──────────────────────────────────
    Connections {
        target: flavorNode
        function onRobotStateChanged(state) {
            // Start the 3s countdown as soon as "done" arrives
            if (state === "done" && window.currentPage === "status" && !window.orderComplete) {
                window.orderComplete = true
                returnTimer.start()
            }
        }
    }

    // ── Background grid ───────────────────────────────────────────────────────
    Canvas {
        anchors.fill: parent; z: 0; opacity: 0.04
        onPaint: {
            var ctx = getContext("2d")
            ctx.strokeStyle = "#5C4A38"; ctx.lineWidth = 1
            for (var x = 0; x < width; x += 30) {
                ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,height); ctx.stroke()
            }
            for (var y = 0; y < height; y += 30) {
                ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(width,y); ctx.stroke()
            }
        }
    }

    // ══════════════════════════════════════════════════════════════════════════
    // PAGE: SELECTOR
    // ══════════════════════════════════════════════════════════════════════════
    Item {
        id: selectorPage
        anchors.fill: parent
        visible: window.currentPage === "selector"
        opacity: visible ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.InOutQuad } }

        Column {
            anchors.top: parent.top; anchors.topMargin: 42
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 6; z: 1

            Text {
                text: "SELECT YOUR FLAVOR"
                font.pixelSize: 11; font.letterSpacing: 5; font.weight: Font.Medium
                color: "#8C7B6A"; anchors.horizontalCenter: parent.horizontalCenter
            }
            Text {
                text: "Scoop Lab"
                font.pixelSize: 38; font.weight: Font.Light
                color: "#2C1F14"; anchors.horizontalCenter: parent.horizontalCenter
            }
        }

        Row {
            id: cardRow
            spacing: 28
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top; anchors.topMargin: 148
            z: 2

            Repeater {
                model: window.flavorOrder
                FlavorButton {
                    flavor: modelData
                    selected: window.activeFlavor === modelData
                    onClicked: {
                        window.activeFlavor = modelData
                    }
                }
            }
        }

        Rectangle {
            height: 32; radius: 16
            width: pillText.implicitWidth + 32
            color: "#2C1F14"
            opacity: window.activeFlavor !== "" ? 1 : 0
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: cardRow.bottom; anchors.topMargin: 18
            z: 2
            Behavior on opacity { NumberAnimation { duration: 300 } }
            Text {
                id: pillText
                anchors.centerIn: parent
                text: window.activeFlavor !== "" ? "✦  " + window.activeFlavor + "  selected" : ""
                font.pixelSize: 11; font.letterSpacing: 1.5; color: "#F5EDD6"
            }
        }

        Rectangle {
            id: nextBtn
            width: 160; height: 42; radius: 21
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: cardRow.bottom; anchors.topMargin: 70
            z: 3

            enabled: window.activeFlavor !== ""
            opacity: enabled ? 1 : 0.35
            Behavior on opacity { NumberAnimation { duration: 250 } }

            color: nextHover.hovered ? "#3D2B1A" : "#2C1F14"
            Behavior on color { ColorAnimation { duration: 180 } }

            scale: nextTap.pressed ? 0.95 : 1.0
            Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutBack } }

            Row {
                anchors.centerIn: parent; spacing: 8
                Text {
                    text: "Confirm Order"
                    font.pixelSize: 13; font.letterSpacing: 1.5; font.weight: Font.Medium
                    color: "#F5EDD6"; anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    text: "→"; font.pixelSize: 15; color: "#D4A96A"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            HoverHandler { id: nextHover }
            TapHandler {
                id: nextTap
                onTapped: {
                    if (window.activeFlavor !== "") {
                        flavorNode.selectFlavor(window.activeFlavor)
                        window.currentPage = "status"
                    }
                }
            }
        }

        Item {
            anchors.left: parent.left; anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 260; z: 1

            CobotArm {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom; anchors.bottomMargin: 8
                width: parent.width; height: 260
                flavor: window.activeFlavor
            }
        }
    }

    // ══════════════════════════════════════════════════════════════════════════
    // PAGE: STATUS
    // ══════════════════════════════════════════════════════════════════════════
    Item {
        id: statusPage
        anchors.fill: parent
        visible: window.currentPage === "status"
        opacity: visible ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 350; easing.type: Easing.InOutQuad } }

        Column {
            anchors.top: parent.top; anchors.topMargin: 42
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 6; z: 1

            Text {
                text: "ORDER IN PROGRESS"
                font.pixelSize: 11; font.letterSpacing: 5; font.weight: Font.Medium
                color: "#8C7B6A"; anchors.horizontalCenter: parent.horizontalCenter
            }
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10
                Text {
                    text: "Scoop Lab"
                    font.pixelSize: 38; font.weight: Font.Light; color: "#2C1F14"
                    anchors.verticalCenter: parent.verticalCenter
                }
                Rectangle {
                    width: flavorTag.implicitWidth + 18; height: 28; radius: 14
                    color: {
                        if (window.activeFlavor === "vanilla")   return "#D4A96A"
                        if (window.activeFlavor === "chocolate") return "#8B5E3C"
                        return "#9B7EC8"
                    }
                    anchors.verticalCenter: parent.verticalCenter
                    Text {
                        id: flavorTag
                        anchors.centerIn: parent
                        text: window.activeFlavor.charAt(0).toUpperCase() + window.activeFlavor.slice(1)
                        font.pixelSize: 12; font.letterSpacing: 1.5; color: "white"
                    }
                }
            }
        }

        StatePanel {
            anchors.left: parent.left; anchors.right: parent.right
            anchors.top: parent.top; anchors.topMargin: 130
            anchors.bottom: backBtn.top; anchors.bottomMargin: 16
            robotState: flavorNode.robotState
            flavor: window.activeFlavor
        }

        Rectangle {
            id: backBtn
            width: 120; height: 38; radius: 19
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom; anchors.bottomMargin: 24
            color: backHover.hovered ? Qt.rgba(0,0,0,0.10) : Qt.rgba(0,0,0,0.06)
            border.color: Qt.rgba(0,0,0,0.12); border.width: 1
            Behavior on color { ColorAnimation { duration: 180 } }

            scale: backTap.pressed ? 0.95 : 1.0
            Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutBack } }

            Row {
                anchors.centerIn: parent; spacing: 8
                Text {
                    text: "←"; font.pixelSize: 15; color: "#8C7B6A"
                    anchors.verticalCenter: parent.verticalCenter
                }
                Text {
                    text: "Back"
                    font.pixelSize: 13; font.letterSpacing: 1; color: "#2C1F14"
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            HoverHandler { id: backHover }
            TapHandler {
                id: backTap
                onTapped: {
                    returnTimer.stop()
                    window.currentPage = "selector"
                    window.activeFlavor = ""
                    window.orderComplete = false
                }
            }
        }
    }

    OpacityAnimator on opacity {
        from: 0; to: 1; duration: 600; easing.type: Easing.OutCubic
    }
}
