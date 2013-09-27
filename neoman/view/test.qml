import QtQuick 1.0

Rectangle {
  width: 200
  height: 200
  color: "red"

  Text {
    text: yubikey.message
    anchors.centerIn: parent
  }
}
