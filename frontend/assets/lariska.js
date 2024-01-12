function render(templateLocator,outputLocator, data) {

      console.log("Rendering template "+ templateLocator + " to " + outputLocator)

      try {
        // Найти элемент шаблона по локатору
        const templateElement = document.querySelector(templateLocator);

        // Проверяем, существует ли элемент шаблона
        if (!templateElement) {
          throw new Error('Элемент шаблона не найден: ' + templateLocator);
        }

        // Найти элемент для вставки результата по локатору
        const outputElement = document.querySelector(outputLocator);

        // Проверяем, существует ли элемент для вставки результата
        if (!outputElement) {
          throw new Error('Элемент для вставки результата не найден: ' + outputLocator);
        }

        // Получаем текст шаблона
        const templateText = templateElement.innerHTML;

        // Попытка скомпилировать шаблон
        var template = Handlebars.compile(templateText);

        // Рендерим шаблон с данными
        const renderedHTML = template(data);

        // Вставляем скомпилированный HTML в output элемент
        outputElement.innerHTML = renderedHTML;

      } catch (error) {
        // Выводим ошибки в консоль
        console.error(error);

      }
}


