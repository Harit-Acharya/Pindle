<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PINDLE Dynamic Readme</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 20px;
    }
    .button-row {
      display: flex;
      justify-content: center;
      margin-bottom: 20px;
    }
    .button-row button {
      margin: 0 10px;
      padding: 10px 20px;
      font-size: 16px;
      cursor: pointer;
    }
    .content-area {
      border: 1px solid #ccc;
      padding: 20px;
      text-align: center;
      min-height: 150px;
    }
  </style>
</head>
<body>
  <h1>PINDLE Dynamic Readme</h1>
  <div class="button-row">
    <button onclick="showContent('categorizer')">Categorizer</button>
    <button onclick="showContent('mounter')">Mounter</button>
    <button onclick="showContent('syncer')">Syncer</button>
  </div>
  <div class="content-area" id="contentArea">
    <p>Select a button above to see more information.</p>
  </div>
  <script>
    function showContent(type) {
      let content = '';
      if (type === 'categorizer') {
        content = `
          <h2>Categorizer</h2>
          <p>This section provides a brief description of the categorizer functionality. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
          <img src="https://via.placeholder.com/300x150?text=Categorizer" alt="Categorizer Image">
        `;
      } else if (type === 'mounter') {
        content = `
          <h2>Mounter</h2>
          <p>This section details the mounter capabilities. Aliquam tincidunt mauris eu risus varius, et pharetra justo cursus.</p>
          <img src="https://via.placeholder.com/300x150?text=Mounter" alt="Mounter Image">
        `;
      } else if (type === 'syncer') {
        content = `
          <h2>Syncer</h2>
          <p>This section describes the syncer component. Quisque consequat sapien ut leo cursus rhoncus, nullam dui mi, vulputate ac metus.</p>
          <img src="https://via.placeholder.com/300x150?text=Syncer" alt="Syncer Image">
        `;
      }
      document.getElementById('contentArea').innerHTML = content;
    }
  </script>
</body>
</html>
