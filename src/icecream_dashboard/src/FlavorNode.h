#pragma once

#include <QObject>
#include <QString>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>
#include <thread>

class FlavorNode : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString selectedFlavor READ selectedFlavor NOTIFY flavorChanged)
    Q_PROPERTY(QString robotState    READ robotState     NOTIFY robotStateChanged)

public:
    explicit FlavorNode(QObject *parent = nullptr);
    ~FlavorNode();

    QString selectedFlavor() const { return m_selectedFlavor; }
    QString robotState()     const { return m_robotState; }

public slots:
    void selectFlavor(const QString &flavor);

signals:
    void flavorChanged(const QString &flavor);
    void robotStateChanged(const QString &state);

private:
    rclcpp::Node::SharedPtr                                m_node;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr    m_publisher;
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr m_stateSub;
    std::thread                                            m_spinThread;
    QString m_selectedFlavor;
    QString m_robotState;
};
