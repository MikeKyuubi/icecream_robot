import QtQuick

// 3-DOF minimalist cobot arm.
// Joint angles specified in world frame (0° = pointing straight up).
//
// Flavor presets:
//   vanilla   (left)  : J1=120°, J2=105°, J3=90°
//   chocolate (center): J1=90°,  J2=90°,  J3=90°
//   mixed     (right) : J1=60°,  J2=75°,  J3=90°
//
// Local QML rotation per joint:
//   base   local = -(worldJ1 - 90)
//   elbow1 local = -(worldJ2 - worldJ1)
//   elbow2 local = -(worldJ3 - worldJ2)

Item {
    id: root

    property string flavor: ""

    width: 300
    height: 320

    // ── Colours ───────────────────────────────────────────────────────────────
    readonly property color clrBase:    "#D8D2CA"
    readonly property color clrSeg1:    "#C8C2BA"
    readonly property color clrSeg2:    "#DEDAD4"
    readonly property color clrSeg3:    "#E8E4DE"
    readonly property color clrJoint:   "#B8B2AA"
    readonly property color clrBorder:  "#A09A92"
    readonly property color clrGripper: "#9A9490"

    // ── World-frame angle presets ─────────────────────────────────────────────
    readonly property var presets: ({
        "vanilla":   { j1: 135, j2: 120, j3: 100 },
        "chocolate": { j1:  90, j2:  90, j3: 90 },
        "mixed":     { j1:  45, j2:  60, j3: 80 }
    })

    // ── Animated local joint angles ───────────────────────────────────────────
    property real baseAngle:   0
    property real elbow1Angle: 0
    property real elbow2Angle: 0

    Behavior on baseAngle   { NumberAnimation { duration: 750; easing.type: Easing.InOutCubic } }
    Behavior on elbow1Angle { NumberAnimation { duration: 750; easing.type: Easing.InOutCubic } }
    Behavior on elbow2Angle { NumberAnimation { duration: 750; easing.type: Easing.InOutCubic } }

    function applyPreset(f) {
        if (!presets[f]) return
        var p = presets[f]
        baseAngle   = -(p.j1 - 90)
        elbow1Angle = -(p.j2 - p.j1)
        elbow2Angle = -(p.j3 - p.j2)
    }

    onFlavorChanged: applyPreset(flavor)
    Component.onCompleted: applyPreset(flavor)

    // ── Base plate ────────────────────────────────────────────────────────────
    Rectangle {
        id: basePlate
        width: 64; height: 18
        radius: 9
        color: root.clrBase
        border.color: root.clrBorder; border.width: 1
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom

        Rectangle {
            width: 10; height: 10; radius: 5
            color: root.clrJoint
            border.color: root.clrBorder; border.width: 1
            anchors.centerIn: parent
        }
    }

    // ── Joint 0 — base pivot ──────────────────────────────────────────────────
    Item {
        id: joint0
        width: 0; height: 0
        anchors.horizontalCenter: basePlate.horizontalCenter
        anchors.bottom: basePlate.top
        anchors.bottomMargin: 2
        rotation: root.baseAngle
        transformOrigin: Item.Center

        // ── Segment 1 ─────────────────────────────────────────────────────────
        Rectangle {
            id: seg1
            width: 16; height: 110
            radius: 8
            color: root.clrSeg1
            border.color: root.clrBorder; border.width: 1
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom

            Rectangle {
                width: 6; height: parent.height * 0.55
                radius: 3
                color: Qt.rgba(1,1,1,0.12)
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 12
            }

            // Joint 1 disc
            Rectangle {
                width: 22; height: 22; radius: 11
                color: root.clrJoint
                border.color: root.clrBorder; border.width: 1.5
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: -5
                z: 2
                Rectangle { width: 8; height: 8; radius: 4; color: root.clrBase; anchors.centerIn: parent }
            }

            // ── Joint 1 pivot ─────────────────────────────────────────────────
            Item {
                id: joint1
                width: 0; height: 0
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 6
                rotation: root.elbow1Angle
                transformOrigin: Item.Center

                // ── Segment 2 ─────────────────────────────────────────────────
                Rectangle {
                    id: seg2
                    width: 13; height: 88
                    radius: 6
                    color: root.clrSeg2
                    border.color: root.clrBorder; border.width: 1
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: parent.bottom

                    Rectangle {
                        width: 5; height: parent.height * 0.5
                        radius: 2
                        color: Qt.rgba(1,1,1,0.10)
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        anchors.topMargin: 10
                    }

                    // Joint 2 disc
                    Rectangle {
                        width: 18; height: 18; radius: 9
                        color: root.clrJoint
                        border.color: root.clrBorder; border.width: 1.5
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        anchors.topMargin: -4
                        z: 2
                        Rectangle { width: 6; height: 6; radius: 3; color: root.clrBase; anchors.centerIn: parent }
                    }

                    // ── Joint 2 pivot ─────────────────────────────────────────
                    Item {
                        id: joint2
                        width: 0; height: 0
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        anchors.topMargin: 5
                        rotation: root.elbow2Angle
                        transformOrigin: Item.Center

                        // ── Segment 3 ─────────────────────────────────────────
                        Rectangle {
                            id: seg3
                            width: 10; height: 60
                            radius: 5
                            color: root.clrSeg3
                            border.color: root.clrBorder; border.width: 1
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom

                            // Joint 3 disc
                            Rectangle {
                                width: 14; height: 14; radius: 7
                                color: root.clrJoint
                                border.color: root.clrBorder; border.width: 1
                                anchors.horizontalCenter: parent.horizontalCenter
                                anchors.top: parent.top
                                anchors.topMargin: -3
                                z: 2
                                Rectangle { width: 5; height: 5; radius: 2.5; color: root.clrBase; anchors.centerIn: parent }
                            }

                            // ── Gripper ───────────────────────────────────────
                            Item {
                                width: 28; height: 22
                                anchors.horizontalCenter: parent.horizontalCenter
                                anchors.top: parent.top
                                anchors.topMargin: -20

                                Rectangle {
                                    width: 5; height: 20; radius: 2.5
                                    color: root.clrGripper
                                    border.color: root.clrBorder; border.width: 1
                                    anchors.left: parent.left
                                    anchors.top: parent.top; anchors.topMargin: 4
                                }
                                Rectangle {
                                    width: 5; height: 20; radius: 2.5
                                    color: root.clrGripper
                                    border.color: root.clrBorder; border.width: 1
                                    anchors.right: parent.right
                                    anchors.top: parent.top; anchors.topMargin: 4
                                }
                                Rectangle {
                                    width: 24; height: 10; radius: 5
                                    color: root.clrJoint
                                    border.color: root.clrBorder; border.width: 1
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    anchors.bottom: parent.bottom
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
