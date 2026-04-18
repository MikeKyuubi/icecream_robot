import QtQuick
import QtQuick.Window

Item {
    id: root

    property string flavor: "vanilla"
    property bool selected: false
    signal clicked()

    readonly property var palette: ({
        "vanilla":   { base: "#FEFAF0", border: "#D4A96A", label: "#7A5C2E" },
        "chocolate": { base: "#2A1A0E", border: "#8B5E3C", label: "#D4C4B4" },
        "mixed":     { base: "#F5F0FA", border: "#9B7EC8", label: "#5A3E7A" }
    })

    readonly property var colors: palette[flavor]
    readonly property var imageMap: ({
        "vanilla":   "qrc:/IceCreamDashboard/resources/Vanilla.png",
        "chocolate": "qrc:/IceCreamDashboard/resources/Chocolate.png",
        "mixed":     "qrc:/IceCreamDashboard/resources/Mixed.png"
    })

    width: 150
    height: 200

    Rectangle {
        id: card
        anchors.fill: parent
        radius: 24
        color: root.colors.base
        border.color: root.selected ? root.colors.border : Qt.rgba(0,0,0,0.08)
        border.width: root.selected ? 2.5 : 1.5

        scale: root.selected ? 1.07 : (hoverHandler.hovered ? 1.03 : 1.0)

        Behavior on scale {
            NumberAnimation { duration: 220; easing.type: Easing.OutBack }
        }
        Behavior on border.color {
            ColorAnimation { duration: 200 }
        }

        // Glow ring when selected
        Rectangle {
            anchors.fill: parent
            anchors.margins: -4
            radius: parent.radius + 4
            color: "transparent"
            border.color: root.colors.border
            border.width: root.selected ? 1 : 0
            opacity: 0.35
            Behavior on border.width { NumberAnimation { duration: 200 } }
        }

        // Ice cream image
        Image {
            id: scoopImage
            source: root.imageMap[root.flavor]
            width: 100
            height: 110
            fillMode: Image.PreserveAspectFit
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: 18
            smooth: true
            antialiasing: true

            NumberAnimation on scale {
                id: bounceAnim
                running: false
                from: 1.0; to: 1.12
                duration: 150
                easing.type: Easing.OutQuad
                onFinished: reverseAnim.start()
            }
            NumberAnimation on scale {
                id: reverseAnim
                running: false
                from: 1.12; to: 1.0
                duration: 180
                easing.type: Easing.InOutQuad
            }
        }

        // Flavor label
        Text {
            text: root.flavor.charAt(0).toUpperCase() + root.flavor.slice(1)
            font.pixelSize: 13
            font.letterSpacing: 2.5
            font.weight: Font.Medium
            color: root.colors.label
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 18
        }

        HoverHandler { id: hoverHandler }

        TapHandler {
            onTapped: {
                bounceAnim.start()
                root.clicked()
            }
        }
    }

    onSelectedChanged: {
        if (selected) bounceAnim.start()
    }
}
