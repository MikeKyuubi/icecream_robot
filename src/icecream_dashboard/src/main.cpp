#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include "FlavorNode.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    app.setApplicationName("IceCream Dashboard");
    app.setOrganizationName("ROS2 Demo");

    // Create the ROS2 node and expose it to QML
    FlavorNode flavorNode;

    QQmlApplicationEngine engine;
    engine.rootContext()->setContextProperty("flavorNode", &flavorNode);

    const QUrl url(u"qrc:/IceCreamDashboard/qml/Main.qml"_qs);
    QObject::connect(
        &engine, &QQmlApplicationEngine::objectCreated,
        &app, [url](QObject *obj, const QUrl &objUrl) {
            if (!obj && url == objUrl)
                QCoreApplication::exit(-1);
        },
        Qt::QueuedConnection
    );
    engine.load(url);

    return app.exec();
}