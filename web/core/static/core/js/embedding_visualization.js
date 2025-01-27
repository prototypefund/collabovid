const EmbeddingVisualization = function () {

        const paperProperties = {width: 0.005, height: 0.005, depth: 0.005, color: 0x5475a1};
        const atlasImage = {cols: 10, rows: 10};
        const mod = function mod(n, m) {
            return ((n % m) + m) % m;
        };
        atlasImage.width = paperProperties.width * atlasImage.cols;
        atlasImage.height = paperProperties.height * atlasImage.rows;

        this.buildGeometry = function (papers, yRadians) {
            const geometry = new THREE.Geometry();

            for (let i = 0; i < papers.length; i++) {
                let paper = papers[i];

                let coords = {
                    x: paper.point[0],
                    y: paper.point[1],
                    z: paper.point[2] + 1
                };

                geometry.vertices.push(
                    new THREE.Vector3(
                        coords.x,
                        coords.y,
                        coords.z
                    ),
                    new THREE.Vector3(
                        coords.x + paperProperties.width * Math.cos(yRadians),
                        coords.y,
                        coords.z + paperProperties.width * Math.sin(yRadians)
                    ),
                    new THREE.Vector3(
                        coords.x + paperProperties.width * Math.cos(yRadians),
                        coords.y + paperProperties.height,
                        coords.z + paperProperties.width * Math.sin(yRadians)
                    ),
                    new THREE.Vector3(
                        coords.x,
                        coords.y + paperProperties.height,
                        coords.z
                    )
                );
                let color = this.getColorForPaper(paper);
                let faces = [
                    [0, 1, 2], [0, 2, 3],
                ];
                let nVertices = 4;
                for (let j = 0; j < faces.length; j++) {
                    let indices = faces[j];
                    let face = new THREE.Face3(
                        geometry.vertices.length - (nVertices - indices[0]),
                        geometry.vertices.length - (nVertices - indices[1]),
                        geometry.vertices.length - (nVertices - indices[2])
                    );
                    face.color = new THREE.Color(color);
                    face.materialIndex = 0;
                    face.origMaterialIndex = 0;
                    geometry.faces.push(face);
                }

                // find image coordinates in atlas image
                let idx = i % (atlasImage.rows * atlasImage.cols);
                let xOffset = (idx % atlasImage.rows) * (paperProperties.width / atlasImage.width);
                let yOffset = Math.floor(idx / atlasImage.cols) * (paperProperties.height / atlasImage.height);
                let xDistance = paperProperties.width / atlasImage.width;
                let yDistance = paperProperties.height / atlasImage.height;
                geometry.faceVertexUvs[0].push([
                    new THREE.Vector2(xOffset, yOffset),
                    new THREE.Vector2(xOffset + xDistance, yOffset),
                    new THREE.Vector2(xOffset + xDistance, yOffset + yDistance)
                ]);
                geometry.faceVertexUvs[0].push([
                    new THREE.Vector2(xOffset, yOffset),
                    new THREE.Vector2(xOffset + xDistance, yOffset + yDistance),
                    new THREE.Vector2(xOffset, yOffset + yDistance)
                ]);

            }

            //geometry.center();

            return geometry;
        };

        this.refreshSize = function () {
            const container = document.getElementById('canvas-container');
            this.camera.aspect = container.offsetWidth / container.offsetHeight;
            this.camera.updateProjectionMatrix();
            this.controls.update();
            this.renderer.setSize(container.offsetWidth, container.offsetHeight);
        };

        this.renderEmbeddings = function (canvas, onSelected, options, callback) {
            let fieldOfView = 75;
            let scope = this;
            let aspectRatio = canvas.offsetWidth / canvas.offsetHeight;
            let nearPlane = 0.001;
            let farPlane = 1000;

            scope.colors = options.categoryColors;

            let camera = new THREE.PerspectiveCamera(
                fieldOfView, aspectRatio, nearPlane, farPlane
            );
            camera.position.z = 2.5;
            camera.position.x = 0;

            let renderer = new THREE.WebGLRenderer({canvas: canvas, alpha: true});
            const container = document.getElementById('canvas-container');
            renderer.setSize(container.offsetWidth, container.offsetHeight);

            let scene = new THREE.Scene();
            scene.background = null;

            let manager = new THREE.LoadingManager();
            manager.onStart = function () {
                $('#embedding-visualization-container').hide();
                $('#visualization-loader').show();
            }
            let loader = new THREE.FileLoader(manager);

            loader.load(options.fileUrl, function (data) {
                $('#embedding-visualization-container').css('visibility', 'visible').show();
                $('#visualization-loader').hide();

                let paperData = JSON.parse(data);
                let papers = paperData.papers;
                let geometry = scope.buildGeometry(papers, 0);
                let loader = new THREE.TextureLoader();
                let url = options.imageUrl;

                // materials with different level of opacity to change opacity for individual faces
                let opacMaterial = new THREE.MeshBasicMaterial({
                    transparent: true,
                    opacity: 0.1,
                    map: loader.load(url),
                    vertexColors: THREE.VertexColors
                });
                let halfOpacMaterial = new THREE.MeshBasicMaterial({
                    transparent: true,
                    opacity: 0.5,
                    map: loader.load(url),
                    vertexColors: THREE.VertexColors
                });
                let solidMaterial = new THREE.MeshBasicMaterial({
                    transparent: false,
                    map: loader.load(url),
                    vertexColors: THREE.VertexColors
                });
                let hiddenMaterial = new THREE.MeshBasicMaterial({
                    transparent: true,
                    opacity: 0.0,
                    map: loader.load(url),
                    vertexColors: THREE.VertexColors
                });
                let material = new THREE.MultiMaterial([solidMaterial, halfOpacMaterial, opacMaterial, hiddenMaterial]);
                scope.hiddenMaterialIndex = 3;

                let mesh = new THREE.Mesh(geometry, material);
                scene.add(mesh);

                let controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.zoomSpeed = options.zoomSpeed;
                controls.panSpeed = options.panSpeed;

                controls.enableRotate = false;
                controls.screenSpacePanning = true;
                controls.mouseButtons = {
                    LEFT: THREE.MOUSE.PAN,
                    MIDDLE: THREE.MOUSE.DOLLY,
                    RIGHT: THREE.MOUSE.DOLLY
                };
                controls.touches = {
                    ONE: THREE.TOUCH.PAN,
                    TWO: THREE.TOUCH.DOLLY_PAN
                };
                controls.update();

                // handle resize of window
                window.addEventListener('resize', function () {
                    scope.refreshSize();
                });

                window.addEventListener('orientationchange', function () {
                    scope.refreshSize();
                });

                // setup the light
                let light = new THREE.PointLight(0xffffff, 1, 10);
                light.position.set(1, 1, 10);
                scene.add(light);

                // animation loop
                function animate(time) {
                    requestAnimationFrame(animate);
                    TWEEN.update(time);
                    renderer.render(scene, camera);
                    if (!scope.animating) {
                        controls.update();
                    }
                }

                requestAnimationFrame(animate);


                let raycaster = new THREE.Raycaster();
                const facesPerPoint = 2;

                function intersectEvent(x, y, callback_intersect = null, callback_no_intersect = null) {
                    if (window.visualizationEventRunning) {
                        return;
                    }

                    let rect = canvas.getBoundingClientRect();
                    x = x - rect.left;
                    y = y - rect.top;
                    let mouse = new THREE.Vector3();
                    mouse.x = ((x / canvas.clientWidth) * 2) - 1;
                    mouse.y = (-(y / canvas.clientHeight) * 2) + 1;
                    raycaster.setFromCamera(mouse, camera);
                    let intersects = raycaster.intersectObjects(scene.children);
                    if (intersects.length > 0) {

                        for (let i = 0; i < intersects.length; i++) {
                            let faceIndex = intersects[i].faceIndex;

                            if (scope.geometry.faces[faceIndex].materialIndex !== scope.hiddenMaterialIndex) {
                                let pointIndex = Math.floor(faceIndex / facesPerPoint);

                                if (callback_intersect) callback_intersect(pointIndex, scope.papers[pointIndex]);
                                return;
                            }
                        }

                    }

                    if (callback_no_intersect) callback_no_intersect();
                }

                // setup listener that only fires on a single click event (no dragging etc.)
                const delta = 6;
                let startX;
                let startY;
                let mouseDown = false;
                renderer.domElement.addEventListener('mousedown', function (event) {
                    startX = event.pageX;
                    startY = event.pageY;
                    mouseDown = true;

                    if (scope.onMouseOverCallback) {
                        scope.onMouseOverCallback();
                    }
                });
                renderer.domElement.addEventListener('mouseup', function (event) {
                    const diffX = Math.abs(event.pageX - startX);
                    const diffY = Math.abs(event.pageY - startY);
                    mouseDown = false;

                    if (diffX < delta && diffY < delta) {
                        intersectEvent(event.clientX, event.clientY, onSelected, function () {
                            scope.deselectAll();
                        });
                    }
                });

                renderer.domElement.addEventListener('mousemove', function (event) {
                    if (mouseDown) {
                        scope.onHoverCallback();
                    } else {
                        intersectEvent(event.clientX, event.clientY, scope.onHoverCallback, scope.onHoverCallback);
                        if (scope.onMouseOverCallback) {
                            scope.onMouseOverCallback();
                        }
                    }
                    {
                    }
                });

                renderer.domElement.addEventListener('touchstart', function (event) {
                    if (scope.onTouchCallback) {
                        scope.onTouchCallback();
                    }

                    startX = event.changedTouches[0].pageX;
                    startY = event.changedTouches[0].pageY;
                });


                renderer.domElement.addEventListener('touchend', function (event) {
                    const diffX = Math.abs(event.changedTouches[0].pageX - startX);
                    const diffY = Math.abs(event.changedTouches[0].pageY - startY);

                    if (diffX < delta && diffY < delta) {
                        intersectEvent(event.changedTouches[0].clientX, event.changedTouches[0].clientY, onSelected, function () {
                            scope.deselectAll();
                        });
                    }
                });

                for (let i = 0; i < papers.length; i++) {
                    papers[i].published_at = moment(papers[i].published_at, "YYYY-MM-DD")
                }


                scope.geometry = geometry;
                scope.renderer = renderer;
                scope.scene = scene;
                scope.papers = papers;
                scope.controls = controls;
                scope.material = material;
                scope.camera = camera;
                scope.paperData = paperData;
                scope.currentRotationStep = 0;
                scope.rotationMaxSteps = 32;

                const bbox = new THREE.Box3().setFromObject(scope.scene);
                const offset = new THREE.Vector3();
                bbox.getCenter(offset).negate();

                scope.geometryOffset = offset;
                scope.geometry.center();

                scope.viewArea(paperData.means[0] + scope.geometryOffset.x, paperData.means[1] + scope.geometryOffset.y, paperData.means[2] + scope.geometryOffset.z + 2.5);

                if (callback) {
                    callback();
                }
            })
        }
        ;

        this.onHover = function (callback) {
            this.onHoverCallback = callback;
        };

        this.onTouch = function (callback) {
            this.onTouchCallback = callback;
        };

        this.onMouseOver = function (callback) {
            this.onMouseOverCallback = callback;
        };

        this.onDeselect = function (callback) {
            this.onDeselectCallback = callback;
        };

        this.computeNeighbors = function (paper, n) {
            let min_distances = new Array(n).fill(null);
            let min_indices = new Array(n).fill(null);
            for (let i = 0; i < this.papers.length; i++) {
                if (paper === this.papers[i]) {
                    continue;
                }
                let isHidden = false;
                let faceStartIndex = i * 2;
                if (this.geometry.faces[faceStartIndex].materialIndex === this.hiddenMaterialIndex) {
                    continue;
                }

                let other = this.papers[i];
                let distance = math.distance(paper.point, other.point);
                let added = false;
                for (let j = 0; j < min_indices.length; j++) {
                    if (min_distances[j] == null) {
                        min_distances[j] = distance;
                        min_indices[j] = i;
                        added = true;
                        break
                    }
                }
                if (!added) {
                    let max_distance = 0;
                    let max_j = 0;
                    for (let j = 0; j < min_indices.length; j++) {
                        if (min_distances[j] > max_distance) {
                            max_distance = min_distances[j];
                            max_j = j;
                        }
                    }

                    if (distance < max_distance) {
                        min_distances[max_j] = distance;
                        min_indices[max_j] = i;
                    }
                }
            }
            return min_indices
        };

        this.getColorForPaper = function (paper) {
            let color = 0xffffff;
            const category = paper.top_category;
            if (category !== undefined) {
                color = this.colors[category]
            }
            return color;
        };


        this.deselectAll = function () {
            for (let i = 0; i < this.papers.length; i++) {
                let color = this.getColorForPaper(this.papers[i]);
                let materialIndex = 0;
                let faceStartIndex = i * 2;
                for (let idx = faceStartIndex; idx < faceStartIndex + 2; idx++) {
                    this.geometry.faces[idx].color = new THREE.Color(color);
                    this.geometry.faces[idx].origMaterialIndex = materialIndex;

                    if (this.geometry.faces[idx].materialIndex !== this.hiddenMaterialIndex) {
                        this.geometry.faces[idx].materialIndex = materialIndex;
                    }

                }
            }
            this.geometry.colorsNeedUpdate = true;
            this.geometry.elementsNeedUpdate = true;
            this.renderer.render(this.scene, this.camera);
            if (this.onDeselectCallback) {
                this.onDeselectCallback();
            }
        };


        this.selectPaper = function (paperIndex, neighborIndices) {
            for (let i = 0; i < this.papers.length; i++) {
                let color = 0xffffff;
                let materialIndex = 2;
                if (neighborIndices.includes(i)) {
                    color = 0xcc7a00;
                    materialIndex = 1;
                }
                if (paperIndex === i) {
                    color = 0xffc266;
                    materialIndex = 0
                }
                let faceStartIndex = i * 2;
                for (let idx = faceStartIndex; idx < faceStartIndex + 2; idx++) {
                    this.geometry.faces[idx].color = new THREE.Color(color);
                    this.geometry.faces[idx].origMaterialIndex = materialIndex;
                    if (this.geometry.faces[idx].materialIndex !== this.hiddenMaterialIndex) {
                        this.geometry.faces[idx].materialIndex = materialIndex;
                    }
                }
            }
            this.geometry.colorsNeedUpdate = true;
            this.geometry.elementsNeedUpdate = true;
        };

        this.viewArea = function (x, y, z) {
            this.camera.position.x = x;
            this.camera.position.y = y;
            this.camera.position.z = z;
            this.controls.target.set(x, y, z - 5);
            this.camera.lookAt(x, y, z - 5);
            this.camera.rotation.z = 0;
            this.camera.rotation.x = 0;
            this.camera.rotation.y = 0;
            this.camera.updateProjectionMatrix();
        };

        this.rotate = function (left) {

            if (left)
                this.currentRotationStep = mod(this.currentRotationStep + 1, this.rotationMaxSteps);
            else
                this.currentRotationStep = mod(this.currentRotationStep - 1, this.rotationMaxSteps);

            const yRotation = (this.currentRotationStep / this.rotationMaxSteps) * 2 * Math.PI;

            const geometry = this.buildGeometry(this.papers, yRotation);
            geometry.center();

            this.geometry.vertices = geometry.vertices;
            this.geometry.rotateY(yRotation);
            this.geometry.colorsNeedUpdate = true;
            this.geometry.elementsNeedUpdate = true;
        };


        this.hidePapers = function (dois) {
            for (let i = 0; i < this.papers.length; i++) {

                const isHidden = dois.has(this.papers[i].doi);

                let faceStartIndex = i * 2;
                for (let idx = faceStartIndex; idx < faceStartIndex + 2; idx++) {
                    if (isHidden) {
                        this.geometry.faces[idx].materialIndex = this.hiddenMaterialIndex; // Hide
                    } else {
                        this.geometry.faces[idx].materialIndex = this.geometry.faces[idx].origMaterialIndex
                    }
                }
            }

            this.geometry.colorsNeedUpdate = true;
            this.geometry.elementsNeedUpdate = true;
        };


        this.selectPapers = function (dois, selectionColor, recolorNonSelectedExisting, focusOnNewLocation) {
            let minCoordinates = new Array(3).fill(100000);
            let maxCoordinates = new Array(3).fill(-10000);

            const defaultColor = new THREE.Color(0xffffff);
            const selectedColor = new THREE.Color(selectionColor);

            for (let i = 0; i < this.papers.length; i++) {
                let color = defaultColor;
                let materialIndex = 2;
                if (dois.has(this.papers[i].doi)) {
                    color = selectedColor;
                    materialIndex = 0;
                    for (let j = 0; j < 3; j++) {
                        minCoordinates[j] = Math.min(this.papers[i].point[j], minCoordinates[j]);
                        maxCoordinates[j] = Math.max(this.papers[i].point[j], maxCoordinates[j]);
                    }
                }
                let faceStartIndex = i * 2;
                for (let idx = faceStartIndex; idx < faceStartIndex + 2; idx++) {
                    if (recolorNonSelectedExisting || color !== defaultColor) {
                        this.geometry.faces[idx].color = color;
                        this.geometry.faces[idx].origMaterialIndex = materialIndex;
                        if (this.geometry.faces[idx].materialIndex !== this.hiddenMaterialIndex) {
                            this.geometry.faces[idx].materialIndex = materialIndex;
                        }
                    }
                }
            }
            this.geometry.colorsNeedUpdate = true;
            this.geometry.elementsNeedUpdate = true;

            if (focusOnNewLocation) {

                for (let i = 0; i < 3; i++) {
                    minCoordinates[i] = minCoordinates[i] + this.geometryOffset.getComponent(i);
                    maxCoordinates[i] = maxCoordinates[i] + this.geometryOffset.getComponent(i);
                }

                let newX = minCoordinates[0] + (maxCoordinates[0] - minCoordinates[0]) / 2.0;
                let newY = minCoordinates[1] + (maxCoordinates[1] - minCoordinates[1]) / 2.0;
                let newZ = maxCoordinates[2] + 2;

                const coords = {x: this.camera.position.x, y: this.camera.position.y, z: this.camera.position.z};
                this.animating = true;
                const tween = new TWEEN.Tween(coords)
                    .to({
                        x: newX,
                        y: newY,
                        z: newZ
                    }, 1200)
                    .easing(TWEEN.Easing.Quadratic.Out)
                    .onUpdate(() => {
                        this.viewArea(coords.x, coords.y, coords.z)
                    }).onComplete(() => {
                        this.animating = false;
                    }).start();
            }
        }
    }
;