import drawBot

drawBot.size(300, 300)
drawBot.save()
drawBot.fill(1, 0, 0)
drawBot.translate(150, 150)
drawBot.rect(0, 0, 100, 100)
drawBot.save()
drawBot.rotate(45)
drawBot.fill(0, 1, 0)
drawBot.rect(0, 0, 100, 100)
drawBot.restore()
drawBot.restore()
drawBot.rect(0, 0, 100, 100)
