import QtQuick

// ── State Panel ───────────────────────────────────────────────────────────────
// Displays current robot state with a matching animated icon.
// States: "idle" | "grabbing_cup" | "getting_icecream" | "serving" | "done"
// Driven entirely by flavorNode.robotState from ROS2.

Item {
    id: root

    property string robotState: "idle"
    property string flavor: ""

    // ── Palette (matches dashboard) ───────────────────────────────────────────
    readonly property color clrBrown:  "#2C1F14"
    readonly property color clrTan:    "#8C7B6A"
    readonly property color clrCream:  "#F7F4EF"
    readonly property color clrAccent: "#D4A96A"

    readonly property var flavorAccent: ({
        "vanilla":   "#D4A96A",
        "chocolate": "#8B5E3C",
        "mixed":     "#9B7EC8"
    })
    readonly property color activeAccent: flavorAccent[flavor] || clrAccent

    // ── State metadata ────────────────────────────────────────────────────────
    readonly property var stateMeta: ({
        "idle":           { label: "Waiting",          sub: "Select a flavor to begin",      step: 0 },
        "grabbing_cup":   { label: "Grabbing Cup",     sub: "Preparing your container...",   step: 1 },
        "getting_icecream": { label: "Scooping",       sub: "Getting your ice cream...",     step: 2 },
        "serving":        { label: "Serving!",         sub: "Almost ready — enjoy!",         step: 3 },
        "done":           { label: "Done!",            sub: "Your order is ready ✦",         step: 4 }
    })

    readonly property var meta: stateMeta[robotState] || stateMeta["idle"]

    // ── Progress steps ────────────────────────────────────────────────────────
    Row {
        id: progressRow
        spacing: 0
        anchors.top: parent.top
        anchors.topMargin: 32
        anchors.horizontalCenter: parent.horizontalCenter

        Repeater {
            model: ["grabbing_cup", "getting_icecream", "serving", "done"]

            Row {
                spacing: 0

                // Step dot
                Rectangle {
                    width: 28; height: 28; radius: 14
                    color: root.meta.step > index ? root.activeAccent
                         : root.meta.step === index + 1 ? root.activeAccent
                         : Qt.rgba(0,0,0,0.08)
                    border.color: root.meta.step >= index + 1 ? root.activeAccent : Qt.rgba(0,0,0,0.12)
                    border.width: 2

                    Behavior on color { ColorAnimation { duration: 400 } }

                    Text {
                        anchors.centerIn: parent
                        text: index + 1
                        font.pixelSize: 11
                        font.weight: Font.Medium
                        color: root.meta.step >= index + 1 ? "white" : root.clrTan
                        Behavior on color { ColorAnimation { duration: 400 } }
                    }
                }

                // Connector line (skip after last)
                Rectangle {
                    visible: index < 3
                    width: 48; height: 2
                    anchors.verticalCenter: parent ? parent.verticalCenter : undefined
                    color: root.meta.step > index + 1 ? root.activeAccent : Qt.rgba(0,0,0,0.10)
                    Behavior on color { ColorAnimation { duration: 400 } }
                }
            }
        }
    }

    // ── Step labels ────────────────────────────────────────────────────────────
    Row {
        spacing: 0
        anchors.top: progressRow.bottom
        anchors.topMargin: 8
        anchors.horizontalCenter: parent.horizontalCenter

        Repeater {
            model: ["Cup", "Scoop", "Serve", "Done"]
            Text {
                width: 76
                text: modelData
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: 9
                font.letterSpacing: 1.5
                color: root.clrTan
            }
        }
    }

    // ── Animated icon area ────────────────────────────────────────────────────
    Item {
        id: iconArea
        width: 160; height: 160
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: progressRow.bottom
        anchors.topMargin: 60

        // ── IDLE: gentle pulse ring ───────────────────────────────────────────
        Item {
            anchors.fill: parent
            visible: root.robotState === "idle" || root.robotState === ""
            opacity: visible ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 300 } }

            Rectangle {
                width: 80; height: 80; radius: 40
                color: "transparent"
                border.color: root.clrAccent; border.width: 2
                anchors.centerIn: parent

                SequentialAnimation on scale {
                    loops: Animation.Infinite
                    NumberAnimation { to: 1.15; duration: 900; easing.type: Easing.InOutSine }
                    NumberAnimation { to: 1.0;  duration: 900; easing.type: Easing.InOutSine }
                }
                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.3; duration: 900; easing.type: Easing.InOutSine }
                    NumberAnimation { to: 1.0; duration: 900; easing.type: Easing.InOutSine }
                }
            }

            Text {
                anchors.centerIn: parent
                text: "○"
                font.pixelSize: 28
                color: root.clrTan
            }
        }

        // ── GRABBING CUP: cup rising animation ────────────────────────────────
        Item {
            anchors.fill: parent
            visible: root.robotState === "grabbing_cup"
            opacity: visible ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 300 } }

            // Cup body
            Rectangle {
                id: cupBody
                width: 52; height: 64
                radius: 6
                color: "transparent"
                border.color: root.activeAccent; border.width: 3
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                anchors.verticalCenterOffset: 10

                // Cup rim
                Rectangle {
                    width: parent.width + 8; height: 8; radius: 4
                    color: root.activeAccent
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: -4
                }

                SequentialAnimation on anchors.verticalCenterOffset {
                    loops: Animation.Infinite
                    NumberAnimation { to: -4;  duration: 600; easing.type: Easing.OutCubic }
                    NumberAnimation { to: 10;  duration: 600; easing.type: Easing.InCubic }
                }
            }

            // Gripper lines (above cup)
            Repeater {
                model: 3
                Rectangle {
                    width: 4; height: 18; radius: 2
                    color: root.clrTan
                    anchors.verticalCenter: cupBody.top
                    anchors.verticalCenterOffset: -14
                    x: iconArea.width / 2 - 12 + index * 12

                    SequentialAnimation on anchors.verticalCenterOffset {
                        loops: Animation.Infinite
                        NumberAnimation { to: -22; duration: 600; easing.type: Easing.OutCubic }
                        NumberAnimation { to: -14; duration: 600; easing.type: Easing.InCubic }
                    }
                }
            }
        }

        // ── GETTING ICE CREAM: swirl dripping down ────────────────────────────
        Item {
            anchors.fill: parent
            visible: root.robotState === "getting_icecream"
            opacity: visible ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 300 } }

            // Nozzle
            Rectangle {
                width: 20; height: 28; radius: 4
                color: root.clrTan
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 14
            }

            // Ice cream drip
            Rectangle {
                id: drip
                width: 14; height: 0
                radius: 7
                color: root.activeAccent
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 40

                SequentialAnimation on height {
                    loops: Animation.Infinite
                    NumberAnimation { to: 60; duration: 900; easing.type: Easing.InCubic }
                    NumberAnimation { to: 0;  duration: 100 }
                }
                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    NumberAnimation { to: 1.0; duration: 900 }
                    NumberAnimation { to: 0.0; duration: 100 }
                    NumberAnimation { to: 0.0; duration: 200 }
                }
            }

            // Cup at bottom
            Rectangle {
                width: 50; height: 44
                radius: 5
                color: "transparent"
                border.color: root.activeAccent; border.width: 2.5
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 10
            }
        }

        // ── SERVING: checkmark draws in ────────────────────────────────────────
        Item {
            anchors.fill: parent
            visible: root.robotState === "serving"
            opacity: visible ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 300 } }

            // Plate / tray
            Rectangle {
                width: 100; height: 12; radius: 6
                color: root.activeAccent; opacity: 0.4
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 22

                SequentialAnimation on anchors.bottomMargin {
                    loops: Animation.Infinite
                    NumberAnimation { to: 28; duration: 700; easing.type: Easing.OutSine }
                    NumberAnimation { to: 22; duration: 700; easing.type: Easing.InSine }
                }
            }

            // Scoop on tray
            Rectangle {
                width: 52; height: 48; radius: 26
                color: root.activeAccent
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 30

                SequentialAnimation on anchors.bottomMargin {
                    loops: Animation.Infinite
                    NumberAnimation { to: 36; duration: 700; easing.type: Easing.OutSine }
                    NumberAnimation { to: 30; duration: 700; easing.type: Easing.InSine }
                }

                Rectangle {
                    width: 14; height: 10; radius: 7
                    color: "white"; opacity: 0.3
                    anchors { top: parent.top; topMargin: 8; left: parent.left; leftMargin: 10 }
                }
            }
        }

        // ── DONE: celebratory sparkles ────────────────────────────────────────
        Item {
            anchors.fill: parent
            visible: root.robotState === "done"
            opacity: visible ? 1 : 0
            Behavior on opacity { NumberAnimation { duration: 300 } }

            Repeater {
                model: 6
                Rectangle {
                    property real angle: index * 60 * Math.PI / 180
                    property real dist: 52
                    width: 8; height: 8; radius: 4
                    color: root.activeAccent
                    x: iconArea.width  / 2 + Math.cos(angle) * dist - 4
                    y: iconArea.height / 2 + Math.sin(angle) * dist - 4

                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        PauseAnimation { duration: index * 120 }
                        NumberAnimation { to: 1.6; duration: 400; easing.type: Easing.OutBack }
                        NumberAnimation { to: 0.8; duration: 400; easing.type: Easing.InBack }
                    }
                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        PauseAnimation { duration: index * 120 }
                        NumberAnimation { to: 1.0; duration: 400 }
                        NumberAnimation { to: 0.4; duration: 400 }
                    }
                }
            }

            Text {
                anchors.centerIn: parent
                text: "✦"
                font.pixelSize: 36
                color: root.activeAccent

                SequentialAnimation on scale {
                    loops: Animation.Infinite
                    NumberAnimation { to: 1.15; duration: 700; easing.type: Easing.InOutSine }
                    NumberAnimation { to: 1.0;  duration: 700; easing.type: Easing.InOutSine }
                }
            }
        }
    }

    // ── State label ───────────────────────────────────────────────────────────
    Column {
        anchors.top: iconArea.bottom
        anchors.topMargin: 24
        anchors.horizontalCenter: parent.horizontalCenter
        spacing: 8

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.meta.label
            font.pixelSize: 28
            font.weight: Font.Light
            color: root.clrBrown

            Behavior on text {
                SequentialAnimation {
                    NumberAnimation { target: stateLabel; property: "opacity"; to: 0; duration: 150 }
                    NumberAnimation { target: stateLabel; property: "opacity"; to: 1; duration: 150 }
                }
            }
        }

        Text {
            id: stateLabel
            anchors.horizontalCenter: parent.horizontalCenter
            text: root.meta.sub
            font.pixelSize: 13
            font.letterSpacing: 1
            color: root.clrTan
        }
    }

    // ── ROS2 topic badge ──────────────────────────────────────────────────────
    Rectangle {
        height: 26
        width: topicText.implicitWidth + 24
        radius: 13
        color: Qt.rgba(0,0,0,0.06)
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 16

        Text {
            id: topicText
            anchors.centerIn: parent
            text: "⬤  /icecream/robot_state  →  " + (root.robotState || "idle")
            font.pixelSize: 10
            font.letterSpacing: 1
            color: root.clrTan
        }
    }
}
